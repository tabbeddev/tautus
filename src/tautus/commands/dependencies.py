import re
import typing
from pathlib import Path

from tautus.projects.dependencies import find_requested_version
from tautus.utils import run_inside_venv, handle_run_error
from tautus.cli.utils import success
from tautus.cli.colors import Fore, Style
from tautus.projects.project_parser import parse_project_json, dump_project_json


def log_installed(name: str, version: str, noadd: bool):
    if noadd:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed: {Fore.RESET}{name}=={version}{Style.RESET_ALL}"
        )
    else:
        print(
            f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed and added to the manifest: {Fore.RESET}{name}=={version}{Style.RESET_ALL}"
        )


def log_added_manifest(name: str, version: str, noadd: bool):
    if noadd:
        print(
            f"{Fore.CYAN}{Style.BRIGHT}[+]{Style.NORMAL} Added to the manifest: {Fore.RESET}{name}=={version}{Style.RESET_ALL}"
        )
    else:
        log_already_installed(name, version)


def log_already_installed(name: str, version: str):
    print(f"[/]{Style.DIM} Was already installed: {Style.NORMAL}{name}=={version}")


type PipCodes = typing.Literal["already-installed", "successfully-installed"]


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
    ]

    for pattern in patterns:
        match = re.search(pattern[1], output)
        if match:
            return (pattern[0], match.group(2))

    raise RuntimeError("Pip output wasn't understood")


def add(name: str, dev: bool, noadd: bool):
    manifest = parse_project_json(".")
    version = find_requested_version(name, dev, manifest)

    if not version:
        dev_venv_path = Path("tautus-venv")

        args = ["-m", "pip", "install", name]

        if not dev:
            args += ["--target", "python-libs", "--only-binary=:all:"]

        result = run_inside_venv(
            "python", args, dev_venv_path, capture_output=True, log_output=False
        )

        handle_run_error(result, "Pip failed to install the package")

        code, version = _understand_pip_output(result.stdout, name)

        if noadd:
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


def update(name: str | None, dev: bool, noadd: bool):
    return


def remove(name: str, dev: bool, noadd: bool):
    return
