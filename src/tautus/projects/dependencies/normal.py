import os
from shutil import rmtree

import tautus.projects.dependencies.cli as cli
from tautus.cli.utils import drylog, warn
from tautus.cli.colors import Fore, Style
from tautus.projects.dependencies.utils import (
    find_requested_version,
    get_installed_list,
    remove_dependency_from_manifest,
    understand_pip_output,
    handle_pip_output,
)
from tautus.projects.project_parser import (
    check_if_extended,
    dump_project_json,
    parse_project_json,
)
from tautus.utils import run_inside_venv, handle_run_error
from tautus.vars import VENV_PATH, WHEELHOUSE_PATH, INSTALLED_LIBS_PATH


def _download(freezes: list[str], target_arch: str):
    result = run_inside_venv(
        "python",
        [
            "-m",
            "pip",
            "download",
            f"--dest={str(WHEELHOUSE_PATH)}",
            "--platform=manylinux2014_" + target_arch,
            "--python-version=3.8",
            "--only-binary=:all:",
            *freezes,
        ],
        check=False,
        log_output=False,
    )
    handle_run_error(result, "Pip failed to download the dependencies")


def _install(
    freezes: list[str], target_arch: str, dry_run: bool = False, update: bool = False
):
    _download(freezes, target_arch)

    target = INSTALLED_LIBS_PATH / target_arch

    args = [
        "-m",
        "pip",
        "install",
        "--no-index",
        f"--find-links={str(WHEELHOUSE_PATH)}",
        f"--target={str(target)}",
        "--platform=manylinux2014_" + target_arch,
        "--python-version=3.8",
        "--only-binary=:all:",
        *freezes,
    ]
    if update:
        args.insert(3, "--upgrade-strategy=only-if-needed")
        args.insert(3, "--upgrade")

    if dry_run:
        drylog(f'Execute "python {" ".join(args)}" inside venv')
        return target, ""
    else:
        result = run_inside_venv(
            "python",
            args,
            check=False,
            log_output=False,
        )
        handle_run_error(result, "Pip failed to install dependencies from wheelhouse")
        return target, result.stdout


def install_all_deps(target_arch: str):
    manifest = parse_project_json()

    target, _ = _install(manifest["requirements"], target_arch)

    if manifest["tautus_extended"]["cleanup_python_libs"] and target.exists():
        rmtree(target)

    print(
        f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed all non-dev dependencies{Style.RESET_ALL}"
    )
    return target


def add(freezes: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    pip_freezes: list[str] = []
    packages: list[str] = []

    for freeze in freezes:
        _split_name = freeze.rsplit("==", 1)
        package_name = _split_name[0]
        package_version = _split_name[1] if len(_split_name) > 1 else None

        manifest_version = find_requested_version(package_name, False, manifest)

        requested_version = package_version or manifest_version

        if requested_version and manifest_version == requested_version:
            cli.log_already_installed(package_name, requested_version)
            continue

        if requested_version:
            pip_freezes.append(package_name + "==" + requested_version)
        else:
            pip_freezes.append(package_name)
        packages.append(package_name)

    if len(pip_freezes) == 0:
        return

    target, output = _install(pip_freezes, os.uname().machine, dry_run)
    actions = understand_pip_output(output)

    handle_pip_output(actions, packages, manifest, noadd or dry_run, False)

    if not (noadd or dry_run):
        dump_project_json(".", manifest)


def remove(package_names: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    warn(
        "Non-dev requirements can't be directly uninstalled. They will just be removed from the manifest, unless noadd was specified."
    )

    for name in package_names:
        requested_version = find_requested_version(name, False, manifest)
        if requested_version:
            if not (noadd or dry_run):
                remove_dependency_from_manifest(manifest, False, name)
            cli.log_removed_manifest(name, requested_version)
        else:
            cli.log_not_installed(name)

    if not (noadd or dry_run):
        dump_project_json(".", manifest)


def update(package_names: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    pre_installed_list = get_installed_list(VENV_PATH, False)

    if len(package_names) == 0:
        # When no packages are specified, update all
        package_names = [req.rsplit("==", 1)[0] for req in manifest["dev_requirements"]]

    target, output = _install(package_names, os.uname().machine, dry_run, True)
    actions = understand_pip_output(output, pre_installed_list)

    handle_pip_output(actions, package_names, manifest, noadd, False, True)

    if not (noadd or dry_run):
        dump_project_json(".", manifest)
