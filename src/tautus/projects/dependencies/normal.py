import os
from pathlib import Path
from shutil import rmtree

from tautus.cli.utils import drylog
from tautus.cli.colors import Fore, Style
from tautus.projects.dependencies.utils import find_requested_version
from tautus.projects.project_parser import (
    check_if_extended,
    dump_project_json,
    parse_project_json,
)
from tautus.projects.types import ProjectManifest
from tautus.utils import run_inside_venv, handle_run_error
from tautus.vars import WHEELHOUSE_PATH, INSTALLED_LIBS_PATH


def _download(freezes: list[str], target_arch: str):
    result = run_inside_venv(
        "python",
        [
            "-m",
            "pip",
            "download",
            f'--dest="{str(WHEELHOUSE_PATH)}"',
            "--platform=manylinux2014_" + target_arch,
            "--python-version=3.8",
            "--only-binary=:all:",
            *freezes,
        ],
        check=False,
        log_output=False,
    )
    handle_run_error(result, "Pip failed to download the dependencies")


def _install(freezes: list[str], target_arch: str, dry_run: bool = False):
    _download(freezes, target_arch)

    target = INSTALLED_LIBS_PATH / target_arch

    args = [
        "-m",
        "pip",
        "install",
        "--no-index",
        f'--find-links="{str(WHEELHOUSE_PATH)}"',
        f'--target="{str(target)}"',
        "--platform=manylinux2014_" + target_arch,
        "--python-version=3.8",
        "--only-binary=:all:",
        "--upgrade",
        "--upgrade-strategy=only-if-needed",
        *freezes,
    ]

    if dry_run:
        drylog(f'Execute "python {" ".join(args)}" inside venv')
    else:
        result = run_inside_venv(
            "python",
            args,
            check=False,
            log_output=False,
        )
        handle_run_error(result, "Pip failed to install dependencies from wheelhouse")
    return target


def install_all_deps(target_arch: str):
    manifest = parse_project_json()

    target = _install(manifest["requirements"], target_arch)

    if manifest["tautus_extended"]["cleanup_python_libs"] and target.exists():
        rmtree(target)

    print(
        f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed all non-dev dependencies"
    )
    return target


def add(freezes: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    pip_freezes: list[str] = []

    for freeze in freezes:
        _split_name = freeze.rsplit("==", 1)
        package_name = _split_name[0]
        package_version = _split_name[1] if len(_split_name) > 1 else None

        manifest_version = find_requested_version(package_name, False, manifest)

        requested_version = package_version or manifest_version

        if requested_version and manifest_version == requested_version:
            continue

        if requested_version:
            pip_freezes.append(package_name + "==" + requested_version)
        else:
            pip_freezes.append(package_name)

    target = _install(pip_freezes, os.uname().machine, dry_run)

    if not (noadd or dry_run):
        # FIXME: Switch to Understand-Pip-Output approach! See the FIXME
        update_freezes(target, manifest)
        dump_project_json(".", manifest)


def remove(package_names: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    filter(
        lambda r: r.rsplit("==", 1)[0] not in package_names, manifest["requirements"]
    )


# FIXME: TODO: Remove! We can't work with solid freezes. Requirements must only contain explicitly requested packages
def update_freezes(target: Path, manifest: ProjectManifest):
    result = run_inside_venv(
        "python",
        ["-m", "pip", "freeze", "--path", str(target)],
        log_output=False,
        check=False,
    )
    handle_run_error(result, "Pip failed to list installed packages")

    manifest["requirements"] = result.stdout.splitlines()
    print(f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Manifest updated")
