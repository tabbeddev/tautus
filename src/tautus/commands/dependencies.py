import re
import typing
from pathlib import Path

from tautus.projects.dependencies import find_requested_version
from tautus.utils import run_inside_venv, handle_run_error
from tautus.cli.utils import drylog
from tautus.cli.colors import Fore, Style
from tautus.projects.project_parser import (
    ProjectManifest,
    parse_project_json,
    dump_project_json,
    check_if_extended,
)


def log_installed(name: str, version: str, noadd: bool):
    if noadd:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed: {Fore.RESET}{name}=={version}"
        )
    else:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed and added to the manifest: {Fore.RESET}{name}=={version}"
        )


def log_uninstalled(name: str, version: str, noadd: bool):
    if noadd:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[-]{Style.NORMAL} Uninstalled: {Fore.RESET}{name}=={version}"
        )
    else:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[-]{Style.NORMAL} Uninstalled and removed from the manifest: {Fore.RESET}{name}=={version}"
        )


def log_added_manifest(name: str, version: str, noadd: bool):
    if noadd:
        log_already_installed(name, version)
    else:
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


def log_removed_manifest(name: str, version: str, noadd: bool):
    if noadd:
        print(
            f"{Fore.YELLOW}{Style.BRIGHT}[-]{Style.NORMAL} Was requested to be removed without manifest changes: {Fore.RESET}{name}=={version}"
        )
    else:
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
            rf"Requirement already satisfied: ({package_name}) in .+site-packages \((\S*)\)",
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

    raise RuntimeError("Pip output wasn't understood")


def add(name: str, dev: bool, noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    version = find_requested_version(name, dev, manifest)

    check_if_extended(manifest)

    if dry_run:
        drylog(f"Running add command. NoAdd: {noadd}; Dev: {dev}")

    if not version:
        dev_venv_path = Path("tautus-venv")
        args = ["-m", "pip", "install", "--retries", "2", name]

        name = name.rsplit("==", 1)[0]

        if not dev:
            args += ["--target", "python-libs", "--only-binary=:all:"]

        if dry_run:
            drylog(f'Execute "python {" ".join(args)}"')
            code: PipCodes = "successfully-installed"
            version = "1.2.3"
        else:
            result = run_inside_venv(
                "python",
                args,
                dev_venv_path,
                capture_output=True,
                log_output=False,
                check=False,
            )

            handle_run_error(result, "Pip failed to install the package")

            code, version = _understand_pip_output(result.stdout, name)

        if not (noadd or dry_run):
            manifest["dev_requirements" if dev else "requirements"].append(
                name + "==" + version
            )
            dump_project_json(".", manifest)

        if code == "successfully-installed":
            log_installed(name, version, noadd)
        elif code == "already-installed":
            log_added_manifest(name, version, noadd)
    else:
        log_already_installed(name, version)


def _update_package(
    name: str, manifest: ProjectManifest, dev: bool, noadd: bool, dry_run: bool = False
):
    version = find_requested_version(name, dev, manifest)

    if version:
        dev_venv_path = Path("tautus-venv")
        args = ["-m", "pip", "install", "--retries", "2", "--upgrade", name]

        if not dev:
            args += ["--target", "python-libs", "--only-binary=:all:"]

        if dry_run:
            drylog(f'Execute "python {" ".join(args)}"')
            code: PipCodes = "successfully-installed"
            new_version = "1.2.3"
        else:
            result = run_inside_venv(
                "python",
                args,
                dev_venv_path,
                capture_output=True,
                log_output=False,
                check=False,
            )

            handle_run_error(result, "Pip failed to install the package")

            code, new_version = _understand_pip_output(result.stdout, name)

        if version == new_version:
            log_already_up_to_date(name, version)
        elif code == "successfully-installed":
            log_installed(name, new_version, noadd)

            if not (noadd or dry_run):
                req = manifest["dev_requirements" if dev else "requirements"]
                req.remove(f"{name}=={version}")
                req.append(f"{name}=={new_version}")

                dump_project_json(".", manifest)
    else:
        log_not_installed(name)


def update(name: str | None, dev: bool, noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()

    if name:
        return _update_package(name, manifest, dev, noadd, dry_run)
    else:
        requirements = manifest["dev_requirements" if dev else "requirements"].copy()

        for req in requirements:
            req = req.rsplit("==", 1)[0]
            _update_package(req, manifest, dev, noadd, dry_run)


def remove(name: str, dev: bool, noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    version = find_requested_version(name, dev, manifest)

    check_if_extended(manifest)

    if dry_run:
        drylog(f"Running remove command. NoAdd: {noadd}; Dev: {dev}")

    if version and dev:
        dev_venv_path = Path("tautus-venv")
        args = ["-m", "pip", "uninstall", "-y", name]

        if dry_run:
            drylog(f'Execute "python {" ".join(args)}"')
            code: PipCodes = "successfully-uninstalled"
            version = "1.2.3"
        else:
            result = run_inside_venv(
                "python",
                args,
                dev_venv_path,
                capture_output=True,
                log_output=False,
                check=False,
            )

            handle_run_error(result, "Pip failed to uninstall the package")

            code, version = _understand_pip_output(result.stdout, name)

        if code == "successfully-uninstalled":
            log_uninstalled(name, version, noadd)
        elif code == "already-uninstalled":
            log_removed_manifest(name, version, noadd)

    elif version:
        # You can't uninstall with --target, so only remove it from the manifest
        print(
            f"{Fore.YELLOW}Non-dev requirements can't be directly uninstalled. They will just be removed from the manifest, unless noadd was specified.{Style.RESET_ALL}"
        )

        log_removed_manifest(name, version, noadd)
    else:
        log_not_installed(name)

    if version and not (noadd or dry_run):
        if not "==" in name:
            full_name = name + "==" + version
        else:
            full_name = name

        manifest["dev_requirements" if dev else "requirements"].remove(full_name)

        dump_project_json(".", manifest)
