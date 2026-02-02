import os
from pathlib import Path

from tautus.cli.utils import drylog, log, error, success
from tautus.projects.project_parser import parse_project_json
from tautus.projects.create_project import (
    create_venv,
    install_clickable,
    upgrade_pip,
)
from tautus.commands.dependencies import add


def install(dry_run: bool = False):
    log("Installing dependencies")

    if os.path.exists("python-libs"):
        error(
            "python-libs exists. Please delete it manually if you really want to reinstall all dependencies"
        )
        exit(1)

    if os.path.exists("tautus-venv"):
        error(
            "tautus-venv exists. Please delete it manually if you really want to reinstall all dependencies"
        )
        exit(1)

    absolute_path = Path(".").absolute()
    manifest = parse_project_json(absolute_path)

    log("Creating venv...")

    if dry_run:
        drylog(
            f'Creating venv at "{absolute_path}" with name "{manifest["metadata"]["title"]}"'
        )
    else:
        _, venv_python = create_venv(absolute_path, manifest["metadata"]["title"])

    log("Upgrading pip...")

    if dry_run:
        drylog("Upgrading pip...")
    else:
        upgrade_pip(venv_python)  # pyright: ignore[reportPossiblyUnboundVariable]

    log(f"Installing clickable {manifest["clickable_version"]}...")

    if dry_run:
        drylog(
            f'Installing clickable with exact version "{manifest["clickable_version"]}"'
        )
    else:
        install_clickable(
            venv_python,  # pyright: ignore[reportPossiblyUnboundVariable]
            manifest["clickable_version"],
        )

    if manifest["tautus_extended"]:
        log("Installing dependencies")

        for dependency in manifest["requirements"]:
            add(dependency, False, False, dry_run)

        for dependency in manifest["dev_requirements"]:
            add(dependency, True, False, dry_run)

    success("Your project is now ready to go", manifest["metadata"]["title"])
