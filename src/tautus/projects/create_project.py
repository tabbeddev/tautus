import json
import os
import re
import shutil
import subprocess
import venv
import typing
from datetime import datetime
from pathlib import Path


from tautus.cli.utils import error, log, sublog, success
from tautus.projects.project_parser import ProjectManifest
from tautus.utils import (
    copy_file_from_templates,
    get_tmp_path,
    handle_run_error,
    replace_text_in_file,
    run_inside_venv,
)
from tautus.vars import TAUTUS_VERSION
from tautus.cli.colors import Style


def create_venv(absolute_path: Path, title: str):
    venv_path = absolute_path / "tautus-venv"

    venv.create(
        env_dir=str(venv_path), prompt="Tautus: " + title, symlinks=True, with_pip=True
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

    with open(absolute_path / "tautus.json", "w") as file:
        json.dump(tautus_json, file, indent=4)

    current_step += 1

    if basic:
        sublog("Skip merging project with TaUTus project")
    else:
        numbered_log("Merge project with TaUTus project")

        sublog("Creating folders...")
        os.makedirs(absolute_path / "python-libs", exist_ok=True)
        os.makedirs(absolute_path / "qml" / "pages", exist_ok=True)
        os.makedirs(absolute_path / ".vscode", exist_ok=True)

        sublog("Copying files from TaUTus Template...")
        # Add apparmor policy
        copy_file_from_templates(
            "appname.apparmor", absolute_path / (name + ".apparmor")
        )

        # Add QRC files
        copy_file_from_templates("assets.qrc", absolute_path / "assets" / "assets.qrc")
        copy_file_from_templates("qml.qrc", absolute_path / "qml" / "qml.qrc")
        copy_file_from_templates("src.qrc", absolute_path / "src" / "src.qrc")

        # Add C++ related stuff
        copy_file_from_templates("main.cpp", absolute_path / "src" / "main.cpp")
        copy_file_from_templates("CMakeLists.txt", absolute_path / "CMakeLists.txt")

        # Add PageStack example with Python
        copy_file_from_templates("Main.qml", absolute_path / "qml" / "Main.qml")
        copy_file_from_templates(
            "Home.qml", absolute_path / "qml" / "pages" / "Home.qml"
        )

        # Add Python files
        copy_file_from_templates("main.py", absolute_path / "src" / "main.py")
        copy_file_from_templates(
            "tautus_libs.py", absolute_path / "src" / "tautus_libs.py"
        )

        # Add Configs
        copy_file_from_templates(
            "settings.json", absolute_path / ".vscode" / "settings.json"
        )
        copy_file_from_templates(
            "extensions.json", absolute_path / ".vscode" / "extensions.json"
        )
        copy_file_from_templates("gitignore", absolute_path / ".gitignore")

        sublog("Modifying clickable.yaml...")
        # Set builder to plain cpp
        replace_text_in_file(
            absolute_path / "clickable.yaml",
            "builder: pure-qml-cmake",
            "builder: cmake",
        )

        sublog(f"Modifying {name}.desktop.in...")
        # Set Exec to the compiled executable
        replace_text_in_file(
            absolute_path / (name + ".desktop.in"),
            "Exec=qmlscene %U qml/Main.qml",
            "Exec=" + name,
        )

        sublog("Modifying main.cpp...")
        # Add main file
        replace_text_in_file(absolute_path / "src" / "main.cpp", "%%name%%", name)
        replace_text_in_file(
            absolute_path / "src" / "main.cpp", "%%namespace%%", namespace
        )

        sublog("Modifying CMakeLists.txt...")
        replace_text_in_file(absolute_path / "CMakeLists.txt", "%%name%%", name)
        replace_text_in_file(
            absolute_path / "CMakeLists.txt", "%%namespace%%", namespace
        )

        sublog("Modifying Main.qml..")
        replace_text_in_file(absolute_path / "qml" / "Main.qml", "%%name%%", name)
        replace_text_in_file(
            absolute_path / "qml" / "Main.qml", "%%namespace%%", namespace
        )

        sublog("Modifying snapcraft.yaml...")
        replace_text_in_file(
            absolute_path / "snapcraft.yaml",
            "command: usr/lib/qt5/bin/qmlscene $SNAP/qml/Main.qml",
            "command: " + name,
        )

        sublog("Modifying manifest.json.in...")
        replace_text_in_file(
            absolute_path / "manifest.json.in",
            '"version": "1.0.0"',
            '"version": "0.0.1"',
        )

        sublog("Deleting default Python example file...")
        # We don't need it
        os.remove(absolute_path / "src" / "example.py")

    success(
        "\nYour TaUTus app is now ready to go at the directory:", str(absolute_path)
    )
    print(
        Style.DIM
        + "Be sure to report any issues at: https://github.com/tabbeddev/tautus"
    )
