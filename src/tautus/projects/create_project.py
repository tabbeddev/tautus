import os
import re
import shutil
import subprocess
import venv
import typing
from datetime import datetime
from pathlib import Path

from tautus.cli.utils import error, log, sublog, success
from tautus.projects.project_parser import ProjectManifest, dump_project_json
from tautus.projects.extended import extend_project
from tautus.utils import (
    get_tmp_path,
    handle_run_error,
    run_inside_venv,
)
from tautus.vars import TAUTUS_VERSION
from tautus.cli.colors import Style


def create_venv(absolute_path: Path, title: str):
    venv_path = absolute_path / "tautus-venv"

    venv.create(
        env_dir=str(venv_path), prompt="TaUTus: " + title, symlinks=True, with_pip=True
    )

    venv_python = venv_path / "bin" / "python"
    return venv_path, venv_python


def upgrade_pip(venv_python: os.PathLike):
    subprocess.run(
        [venv_python, "-m", "pip", "install", "--retries", "2", "--upgrade", "pip"],
        check=True,
    )


def install_clickable(venv_python: os.PathLike, clickable_version: str | None = None):
    args = [
        venv_python,
        "-m",
        "pip",
        "install",
        "--retries",
        "2",
    ]

    if clickable_version:
        args += ["clickable-ut==" + clickable_version]
    else:
        args.append("clickable-ut")

    subprocess.run(
        args,
        check=True,
    )


def get_clickable_version(venv_path: os.PathLike):
    version_result = run_inside_venv(
        "clickable",
        ["--version"],
        venv_path,
    )
    version_text = version_result.stdout

    version_match = re.search(r"clickable (\d\.\d\.\d)", version_text, re.IGNORECASE)
    if not version_match:
        error(
            "Clickable Test failed: Version pattern wasn't found! TaUTus can't continue."
        )
        exit(1)

    return version_match.group(1)


def create_project(
    title: str,
    name: str,
    namespace: str,
    description: str,
    maintainer: str,
    mail: str,
    license: str,
    dirname: str,
    basic: bool,
    clickable_version: str | None,
):
    def numbered_log(message: str):
        log(f"[Step {current_step}/{total_steps}] {message}")

    if not dirname:
        dirname = "."

    os.makedirs(dirname, exist_ok=True)
    content = os.listdir(dirname)
    if "tautus.pyz" in content:
        content.remove("tautus.pyz")

    absolute_path = Path(dirname).absolute()

    if len(content) != 0:
        error(
            f"The target directory ({absolute_path}) isn't empty. Please check if you specified the right directory and if so empty it. (The file tautus.pyz is ignored)"
        )
        exit(1)

    total_steps = 7
    current_step = 1

    if basic:
        total_steps -= 1

    if clickable_version:
        total_steps -= 1

    # Create venv

    numbered_log("Creating venv...")

    venv_path, venv_python = create_venv(absolute_path, title)
    current_step += 1

    numbered_log("Upgrading pip...")

    upgrade_pip(venv_python)
    current_step += 1

    if clickable_version:
        numbered_log("Installing clickable " + clickable_version + "...")
        install_clickable(venv_python, clickable_version)
    else:
        numbered_log("Installing latest clickable...")
        install_clickable(venv_python)

        current_step += 1

        numbered_log("Testing clickable...")
        clickable_version = get_clickable_version(venv_path)

    tmp_path = get_tmp_path()

    current_step += 1
    numbered_log("Creating clickable project...")

    create_result = run_inside_venv(
        "clickable",
        [
            "create",
            "--title",
            title,
            "--name",
            name,
            "--namespace",
            namespace,
            "--description",
            description,
            "--maintainer",
            maintainer,
            "--mail",
            mail,
            "--license",
            license,
            "--template",
            "python-cmake",
            "--non-interactive",
            "--dir",
            str(tmp_path),
        ],
        venv_path,
        check=False,
        log_output=False,
    )
    handle_run_error(
        create_result,
        "Clickable failed to create the project. Please blame TaUTus first!",
    )

    tmp_clickable_path = (tmp_path / name).absolute()
    if not tmp_clickable_path.exists():
        error("The created clickable project was not found! TaUTus can't continue.")
        exit(1)

    current_step += 1
    numbered_log("Completing basic setup...")

    shutil.copytree(tmp_clickable_path, absolute_path, dirs_exist_ok=True)
    sublog("Copying TaUTus to your new project...")
    shutil.copy("./tautus.pyz", absolute_path)
    shutil.rmtree(tmp_clickable_path)

    tautus_json: ProjectManifest = {
        "tautus_version": TAUTUS_VERSION,
        "clickable_version": typing.cast(str, clickable_version),
        "metadata": {
            "title": title,
            "name": name,
            "namespace": namespace,
            "description": description,
            "maintainer": maintainer,
            "mail": mail,
            "license": license,
            "copyright_year": str(datetime.today().year),
            "version": "0.0.1",
        },
        "tautus_extended": not basic,
        "requirements": [],
        "dev_requirements": [],
        "pre_build_commands": [],
        "pre_release_build_commands": [],
        "qrc": {
            "auto_generate": True,
            "paths": ["qml", "assets", "src", "python-libs"],
        },
    }

    dump_project_json(absolute_path, tautus_json)

    current_step += 1

    if basic:
        sublog("Skip extending project with TaUTus extended")
    else:
        numbered_log("Extending project with TaUTus extended")
        extend_project(name, namespace, absolute_path, True)

    success(
        "\nYour TaUTus app is now ready to go at the directory:", str(absolute_path)
    )
    print(
        Style.DIM
        + "Be sure to report any issues at: https://github.com/tabbeddev/tautus"
    )
