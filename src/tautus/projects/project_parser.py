import os
import json
import subprocess
import tautus.vars
from shutil import rmtree
from pathlib import Path

from tautus.cli.utils import error, sublog, warn
from tautus.utils import copy_file_from_templates, replace_text_in_file
from tautus.projects.types import ProjectManifest as _ProjectManifest


def parse_project_json(path: os.PathLike | str = ".") -> _ProjectManifest:
    project_path = Path(path)
    json_path = project_path / "tautus.json"

    converted = False
    queue_reinstall_venv = False

    with open(json_path, "r") as file:
        content = json.load(file)

    # Add code to add backwards compatability here

    # Move qrc option to new tautus_extended option
    if "qrc" in content and type(content["tautus_extended"]) is bool:
        is_extended = content["tautus_extended"]
        qrc_data = content["qrc"]

        del content["qrc"]
        content["tautus_extended"] = {"is_extended": is_extended, "qrc": qrc_data}

        converted = True

    # Remove "python-libs" from qrc paths to its own option
    if "include_python_libs" not in content["tautus_extended"]:
        include_python_libs = (
            "python-libs" in content["tautus_extended"]["qrc"]["paths"]
        )

        if include_python_libs:
            content["tautus_extended"]["qrc"]["paths"].remove("python-libs")

        content["tautus_extended"]["include_python_libs"] = include_python_libs

        warn(
            "The way how python libraries are included in TaUTus got changed. This requires your tautus-libs.py and your CMakeLists.txt files to be updated."
        )

        python_qrc_path = project_path / "python-libs" / "python.qrc"

        if python_qrc_path.exists():
            os.remove(python_qrc_path)

        copy_file_from_templates(
            "tautus_libs.py", project_path / "src" / "tautus_libs.py"
        )
        replace_text_in_file(
            project_path / "CMakeLists.txt",
            "python-libs/python.qrc",
            "build/python.qrc",
        )

        converted = True

    # Move "python-libs" to "python-libs-[arch]" and symlink back
    # Move from QRC based libraries to Install based libraries
    python_libs_path = project_path / "python-libs"

    if python_libs_path.exists() and not python_libs_path.is_symlink():
        # Move libs
        os.makedirs(project_path / tautus.vars.INSTALLED_LIBS_PATH, exist_ok=True)
        os.makedirs(project_path / tautus.vars.WHEELHOUSE_PATH, exist_ok=True)

        new_libs_path = (
            project_path / tautus.vars.INSTALLED_LIBS_PATH / os.uname().machine
        )

        python_libs_path.move(new_libs_path)

        content["tautus_extended"]["cleanup_python_libs"] = False

        warn(f"The python-libs folder got moved to {new_libs_path}")
        warn("This change is to support build for other platforms")

        # Change inclusion method
        warn(
            "The way how python libraries are included in TaUTus got changed (again). This requires your tautus-libs.py and your CMakeLists.txt files to be updated."
        )

        copy_file_from_templates(
            "tautus_libs.py", project_path / "src" / "tautus_libs.py"
        )
        copy_file_from_templates("CMakeLists.txt", project_path / "CMakeLists.txt")
        replace_text_in_file(
            project_path / "CMakeLists.txt",
            "%%name%%",
            content["metadata"]["name"],
            True,
        )
        replace_text_in_file(
            project_path / "CMakeLists.txt",
            "%%namespace%%",
            content["metadata"]["namespace"],
            True,
        )

        with (project_path / "clickable.yaml").open("a") as f:
            f.write(f"\nenv_vars:\n    TAUTUS_ARCH: {os.uname().machine}")

        (project_path / "build" / "python.zip").unlink(missing_ok=True)
        (project_path / "build" / "python.qrc").unlink(missing_ok=True)

        converted = True

    # Remove legacy Venv
    legacy_venv_path = project_path / "tautus-venv"

    if legacy_venv_path.exists():
        rmtree(legacy_venv_path)

        warn(f"The tautus-venv folder will get moved to {tautus.vars.VENV_PATH}")
        warn("This requires a reinstall of the venv.")
        queue_reinstall_venv = True
        converted = True

    # Save the updates project manifest
    if converted:
        content["tautus_version"] = tautus.vars.MANIFEST_VERSION

        sublog("The project manifest was upgraded. Saving the new version now...")
        dump_project_json(project_path, content)

    if (
        (not "tautus_version" in content)
        or content["tautus_version"] != tautus.vars.MANIFEST_VERSION
    ) and not converted:
        error(
            "TaUTus Manifest versions mismatch: Manifest file version isn't the same as the TaUTus version and file couldn't be converted."
        )
        error(
            "Manifest: "
            + (
                content["tautus_version"]
                if "tautus_version" in content
                else "not-specified"
            )
        )
        error("TaUTus: " + tautus.vars.MANIFEST_VERSION)
        error(
            "\nReminder: TaUTus doesn't update itself. You need to download a new version yourself."
        )
        exit(1)

    if queue_reinstall_venv:
        subprocess.run([str((project_path / "tautus.pyz").absolute()), "install"])

    return content


def dump_project_json(path: os.PathLike | str, manifest: _ProjectManifest):
    json_path = Path(path) / "tautus.json"

    with open(json_path, "w") as file:
        json.dump(manifest, file, indent=4)


def check_if_extended(manifest: _ProjectManifest):
    if manifest["tautus_extended"]["is_extended"]:
        return

    error("This command requires a TaUTus extended project.")
    exit(1)


def check_if_not_extended(manifest: _ProjectManifest):
    if not manifest["tautus_extended"]["is_extended"]:
        return

    error("This command doesn't support a TaUTus extended project.")
    exit(1)
