import os
import json
import typing
from pathlib import Path

from tautus.cli.utils import error, sublog, warn
from tautus.utils import copy_file_from_templates, replace_text_in_file
from tautus.vars import MANIFEST_VERSION


class ProjectMetadata(typing.TypedDict):
    title: str
    name: str
    namespace: str
    description: str
    maintainer: str
    mail: str
    license: str
    copyright_year: str
    version: str


class ProjectExtended(typing.TypedDict):
    is_extended: bool
    qrc: ProjectQRCConfig
    include_python_libs: bool


class ProjectQRCConfig(typing.TypedDict):
    auto_generate: bool
    paths: list[str]


class ProjectManifest(typing.TypedDict):
    tautus_version: str
    clickable_version: str
    metadata: ProjectMetadata
    tautus_extended: ProjectExtended
    requirements: list[str]
    dev_requirements: list[str]
    pre_build_commands: list[str]
    pre_release_build_commands: list[str]


def parse_project_json(path: os.PathLike | str = ".") -> ProjectManifest:
    project_path = Path(path)
    json_path = project_path / "tautus.json"

    converted = False

    with open(json_path, "r") as file:
        content = json.load(file)

    # Add code to add backwards compatability here

    # Move qrc option to new tautus_extended option
    if "qrc" in content and type(content["tautus_extended"]) == bool:
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

    if converted:
        content["tautus_version"] = MANIFEST_VERSION

        sublog("The project manifest was upgraded. Saving the new version now...")
        with open(json_path, "w") as file:
            json.dump(content, file, indent=4)

    if (
        (not "tautus_version" in content)
        or content["tautus_version"] != MANIFEST_VERSION
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
        error("TaUTus: " + MANIFEST_VERSION)
        error(
            "\nReminder: TaUTus doesn't update itself. You need to download a new version yourself."
        )
        exit(1)

    return content


def dump_project_json(path: os.PathLike | str, manifest: ProjectManifest):
    json_path = Path(path) / "tautus.json"

    with open(json_path, "w") as file:
        json.dump(manifest, file, indent=4)


def check_if_extended(manifest: ProjectManifest):
    if manifest["tautus_extended"]["is_extended"]:
        return

    error("This command requires a TaUTus extended project.")
    exit(1)


def check_if_not_extended(manifest: ProjectManifest):
    if not manifest["tautus_extended"]["is_extended"]:
        return

    error("This command doesn't support a TaUTus extended project.")
    exit(1)
