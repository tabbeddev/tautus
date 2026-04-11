import re
import typing
from pathlib import Path

from tautus.projects.dependencies.utils import (
    add_dependency_to_manifest,
    find_installed_version,
    find_requested_version,
    get_installed_list,
    remove_dependency_from_manifest,
)
from tautus.projects.types import ProjectManifest
from tautus.utils import run_inside_venv, handle_run_error
from tautus.cli.utils import drylog, warn
from tautus.cli.colors import Fore, Style
from tautus.projects.project_parser import (
    parse_project_json,
    dump_project_json,
    check_if_extended,
)
from tautus.vars import VENV_PATH


def log_installed(name: str, version: str):
    print(
        f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed: {Fore.RESET}{name}=={version}"
    )


def log_uninstalled(name: str, version: str):
    print(
        f"{Fore.GREEN}{Style.BRIGHT}[-]{Style.NORMAL} Uninstalled: {Fore.RESET}{name}=={version}"
    )


def log_added_manifest(name: str, version: str):
    print(
        f"{Fore.CYAN}{Style.BRIGHT}[+]{Style.NORMAL} Added to the manifest: {Fore.RESET}{name}=={version}"
    )


def log_already_installed(name: str, version: str):
    print(f"[/]{Style.DIM} Was already installed: {Style.NORMAL}{name}=={version}")


def log_already_up_to_date(name: str, version: str):
    print(
        f"{Fore.CYAN}[/]{Style.DIM} Already up-to-date: {Style.RESET_ALL}{name}=={version}"
    )


def log_not_installed(name: str):
    print(f"[/]{Style.DIM} Is not installed: {Style.NORMAL}{name}")


def log_removed_manifest(name: str, version: str):
    print(
        f"{Fore.CYAN}{Style.BRIGHT}[-]{Style.NORMAL} Was removed from the manifest: {Fore.RESET}{name}=={version}"
    )


type PipCodes = typing.Literal[
    "already-installed",
    "successfully-installed",
    "successfully-uninstalled",
    "already-uninstalled",
]


def _understand_pip_output(output: str, package_name: str):
    patterns: list[tuple[PipCodes, str]] = [
        (
            "already-installed",
            rf"WARNING: Target directory .*?({package_name})-(.*?)\.dist-info already exists",
        ),
        (
            "successfully-installed",
            rf"Successfully installed .*?({package_name})-(\S*)",
        ),
        (
            "already-installed",
            rf"Requirement already satisfied: ({package_name}).*? in [^(]* \((\S*)\)",
        ),
        (
            "successfully-uninstalled",
            rf"Successfully uninstalled ({package_name})-(\S*)",
        ),
        (
            "already-uninstalled",
            rf"WARNING: Skipping ({package_name}) as it is not installed.",
        ),
    ]

    for pattern in patterns:
        match = re.search(pattern[1], output, re.IGNORECASE)
        if match:
            return (pattern[0], match.group(2))

    print(output)
    raise RuntimeError("Pip output wasn't understood")


def add(
    target: str,
    dev: bool,
    noadd: bool,
    dry_run: bool = False,
    ignore_comp: bool = False,
    installed_list: dict[str, str] | None = None,
):
    manifest = parse_project_json()
    check_if_extended(manifest)

    dev_venv_path = VENV_PATH

    installed_list = installed_list or get_installed_list(dev_venv_path, dev)

    _split_name = target.rsplit("==", 1)
    package_name = _split_name[0]
    package_version = _split_name[1] if len(_split_name) > 1 else None

    manifest_version = find_requested_version(package_name, dev, manifest)
    installed_version = find_installed_version(package_name, installed_list)

    requested_version = package_version or manifest_version or installed_version

    if ignore_comp and not dev:
        warn(
            "--ignore-compatability was specified. Packages are not garanteed to work with the bundled python interpreter."
        )

    if dry_run:
        drylog(f"Running add command. NoAdd: {noadd}; Dev: {dev}")

    if installed_version and installed_version == requested_version:
        log_already_installed(package_name, installed_version)
    else:
        args = ["-m", "pip", "install", "--retries", "2"]

        if not dev:
            args += ["--target", "python-libs"]
            if not ignore_comp:
                args += ["--only-binary=:all:", "--python-version", "3.8"]

        if requested_version:
            args.append(package_name + "==" + requested_version)
        else:
            args.append(package_name)

        if dry_run:
            drylog(f'Execute "python {" ".join(args)}"')
        else:
            result = run_inside_venv(
                "python",
                args,
                log_output=False,
                check=False,
            )

            handle_run_error(result, "Pip failed to install the package")

            code, installed_version = _understand_pip_output(
                result.stdout, package_name
            )
            if code == "successfully-installed":
                log_installed(package_name, installed_version)
            elif code == "already-installed":
                log_already_installed(package_name, installed_version)

    if (
        not (dry_run or noadd)
        and installed_version
        and manifest_version != installed_version
    ):
        add_dependency_to_manifest(manifest, dev, package_name, installed_version)
        log_added_manifest(package_name, installed_version)
        dump_project_json(".", manifest)


def _update_package(
    package_name: str,
    manifest: ProjectManifest,
    dev: bool,
    noadd: bool,
    installed_list: dict[str, str],
    dry_run: bool = False,
    ignore_comp: bool = False,
):
    manifest_version = find_requested_version(package_name, dev, manifest)
    installed_version = find_installed_version(package_name, installed_list)

    if not installed_version:
        log_not_installed(package_name)
        return

    args = ["-m", "pip", "install", "--retries", "2", "--upgrade", package_name]

    if not dev:
        args += [
            "--target",
            "python-libs",
        ]
        if not ignore_comp:
            args += ["--only-binary=:all:", "--python-version", "3.8"]

    if dry_run:
        drylog(f'Execute "python {" ".join(args)}"')
    else:
        result = run_inside_venv(
            "python",
            args,
            capture_output=True,
            log_output=False,
            check=False,
        )

        handle_run_error(result, "Pip failed to install the package")

        code, new_version = _understand_pip_output(result.stdout, package_name)

        if installed_version == new_version:
            log_already_up_to_date(package_name, new_version)
        elif code == "successfully-installed":
            log_installed(package_name, new_version)

        if not noadd and manifest_version != new_version:
            add_dependency_to_manifest(manifest, dev, package_name, new_version)
            log_added_manifest(package_name, new_version)
            dump_project_json(".", manifest)


def update(
    name: str | None,
    dev: bool,
    noadd: bool,
    dry_run: bool = False,
    ignore_comp: bool = False,
    installed_list: dict[str, str] | None = None,
):
    manifest = parse_project_json()
    check_if_extended(manifest)

    installed_list = installed_list or get_installed_list(VENV_PATH, dev)

    if ignore_comp and not dev:
        warn(
            "--ignore-compatability was specified. Packages are not garanteed to work with the bundled python interpreter."
        )

    if dry_run:
        drylog(f"Running update command. NoAdd: {noadd}; Dev: {dev}")

    if name:
        return _update_package(
            name, manifest, dev, noadd, installed_list, dry_run, ignore_comp
        )
    else:
        requirements = manifest["dev_requirements" if dev else "requirements"].copy()

        for req in requirements:
            req = req.rsplit("==", 1)[0]
            _update_package(
                req, manifest, dev, noadd, installed_list, dry_run, ignore_comp
            )


def remove(
    package_name: str,
    dev: bool,
    noadd: bool,
    dry_run: bool = False,
    installed_list: dict[str, str] | None = None,
):
    manifest = parse_project_json()
    check_if_extended(manifest)

    dev_venv_path = VENV_PATH

    installed_list = installed_list or get_installed_list(dev_venv_path, dev)

    manifest_version = find_requested_version(package_name, dev, manifest)
    installed_version = find_installed_version(package_name, installed_list)

    if dry_run:
        drylog(f"Running remove command. NoAdd: {noadd}; Dev: {dev}")

    if installed_version and dev:
        args = ["-m", "pip", "uninstall", "-y", package_name]

        if dry_run:
            drylog(f'Execute "python {" ".join(args)}"')
        else:
            result = run_inside_venv(
                "python",
                args,
                capture_output=True,
                log_output=False,
                check=False,
            )

            handle_run_error(result, "Pip failed to uninstall the package")

            code, version = _understand_pip_output(result.stdout, package_name)

            if code == "successfully-uninstalled":
                log_uninstalled(package_name, version)
            elif code == "already-uninstalled":
                log_not_installed(package_name)
    elif installed_version:
        # You can't uninstall with --target, so only remove it from the manifest
        # Technically you could remove the all files from the package through the .dist-info folders, but who cares?
        warn(
            "Non-dev requirements can't be directly uninstalled. They will just be removed from the manifest, unless noadd was specified."
        )
    else:
        log_not_installed(package_name)

    if not noadd and manifest_version:
        remove_dependency_from_manifest(manifest, dev, package_name)
        log_removed_manifest(package_name, manifest_version)
        dump_project_json(".", manifest)
