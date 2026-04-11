import os
import shutil
from pathlib import Path

from tautus.cli.utils import drylog, log, success, sublog, warn
from tautus.projects.dependencies.normal import install_all_deps
from tautus.projects.dependencies.utils import get_installed_list
from tautus.projects.project_parser import parse_project_json
from tautus.projects.create_project import (
    create_venv,
    get_clickable_version,
    install_clickable,
    upgrade_pip,
)
from tautus.commands.LEGACY_dependencies import add
from tautus.vars import VENV_PATH


def install(dry_run: bool = False, ignore_comp: bool = False):
    absolute_path = Path(".").absolute()

    venv_path = absolute_path / VENV_PATH
    venv_python = venv_path / "bin" / "python"

    manifest = parse_project_json()

    # Step 1: Venv
    log("Checking venv state...")

    reinstall_venv = False
    if not venv_path.exists():
        warn("Venv does not exist")
        reinstall_venv = True
    elif not venv_python.exists():
        warn("Venv does exist, but the Python instance went missing")
        reinstall_venv = True
    else:
        sublog("Venv does exist")

    if reinstall_venv:
        # Something is wrong with the venv
        # Delete it if it still exists
        if venv_path.exists():
            shutil.rmtree(venv_path)

        if dry_run:
            drylog(f'Creating venv at "{venv_path}"')
        else:
            create_venv(absolute_path, manifest["metadata"]["title"])

    # Step 2: Upgrade Pip
    log("Upgrading Pip...")

    if not dry_run:
        upgrade_pip(venv_python)

    # Step 3: Clickable Version
    log("Checking Clickable version...")

    requested_clickable_version = manifest["clickable_version"]

    if (venv_path / "bin" / "clickable").exists():
        running_clickable_version = get_clickable_version(venv_path)

        if running_clickable_version != requested_clickable_version:
            sublog(
                f"Installing Clickable version {requested_clickable_version} instead of {running_clickable_version}..."
            )
            if not dry_run:
                install_clickable(venv_python, requested_clickable_version)
        else:
            sublog("Clickable version matches")
    else:
        warn("Clickable does not exist")
        sublog(f"Installing Clickable version {requested_clickable_version}...")
        if not dry_run:
            install_clickable(venv_python, requested_clickable_version)

    # Step 4: Dependencies
    if manifest["tautus_extended"]["is_extended"]:
        log("Installing dependencies...")
        install_all_deps(os.uname().machine)

        log("Installing dev dependencies...")
        dev_installed_list = get_installed_list(venv_path, True)

        for dependency in manifest["dev_requirements"]:
            add(dependency, True, True, dry_run, ignore_comp, dev_installed_list)

    success("Your project is now ready to go", manifest["metadata"]["title"])
