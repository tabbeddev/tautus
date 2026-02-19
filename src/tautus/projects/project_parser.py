import os
import json
import typing
from pathlib import Path

from tautus.cli.utils import error, sublog
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
    json_path = Path(path) / "tautus.json"

    converted = False

    with open(json_path, "r") as file:
        content = json.load(file)

    # Add code to add backwards compatability here
    if "qrc" in content and type(content["tautus_extended"]) == bool:
        is_extended = content["tautus_extended"]
        qrc_data = content["qrc"]

        del content["qrc"]
        content["tautus_extended"] = {"is_extended": is_extended, "qrc": qrc_data}

        converted = True

    if converted:
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
