import os
import typing
import json
import re
from pathlib import Path

from tautus.cli.utils import error, log, sublog
from tautus.projects.project_parser import ProjectManifest, parse_project_json
from tautus.utils import handle_run_error, run_inside_venv
from tautus.cli.colors import Style


def pre_build(manifest: ProjectManifest):
    if manifest["qrc"]["auto_generate"]:
        sublog("Generation QRC files...")
        for path in manifest["qrc"]["paths"]:
            directory = Path(".") / path
            qrc_target = directory / (
                (
                    "python"
                    if path == "python-libs" and manifest["tautus_extended"]
                    else path
                )
                + ".qrc"
            )

            discovered_paths: list[str] = []

            sublog(f"- Generating {qrc_target.name}...")

            def traverse_dir(path: Path):
                directory_content = os.listdir(path)

                for content in directory_content:
                    content_path = path / content

                    if content_path.is_dir():
                        traverse_dir(content_path)
                    elif content_path.is_file():
                        if (
                            content_path.name == qrc_target.name
                            or str(content_path) == "src/main.cpp"
                        ):
                            continue

                        discovered_paths.append(str(content_path))

            traverse_dir(directory)

            content = [
                "<!DOCTYPE RCC>\n",
                "<RCC>\n",
                f'    <qresource prefix="/{path}">\n',
                *[
                    f"        <file>{file.removeprefix(path + "/")}</file>\n"
                    for file in discovered_paths
                ],
                "    </qresource>\n",
                "</RCC>\n",
            ]

            with open(qrc_target, "w") as qrc_file:
                qrc_file.writelines(content)

    # Set version numbers
    sublog("Updating version numbers")

    sublog("- Updating manifest.json.in")
    with open("manifest.json.in", "r+") as manifest_file:
        content = json.load(manifest_file)
        content["version"] = manifest["metadata"]["version"]

        manifest_file.seek(0)
        json.dump(content, manifest_file, indent=4)
        manifest_file.truncate()

    sublog("- Updating snapcraft.yaml")
    with open("snapcraft.yaml", "r+") as snapcraft_file:
        content = snapcraft_file.read()
        new_content = re.sub(
            r"^version: [\d\.]*$",
            "version: " + manifest["metadata"]["version"],
            content,
            1,
            re.MULTILINE,
        )

        snapcraft_file.seek(0)
        snapcraft_file.write(new_content)
        snapcraft_file.truncate()


def build(
    target: typing.Literal["desktop", "device", "publish"], api: str | None = None
):
    log("Preparing build")
    manifest = parse_project_json(".")

    pre_build(manifest)

    log("Building for target: " + target.capitalize())

    dev_venv_path = Path("tautus-venv")

    if target == "desktop":
        build_result = run_inside_venv(
            "clickable", ["desktop"], dev_venv_path, check=False
        )
    elif target == "device":
        args = ["build", "--skip-review", "--arch", "detect"]

        build_result = run_inside_venv(
            "clickable",
            args,
            dev_venv_path,
            check=False,
        )
    elif target == "publish":
        if not api and "OPENSTORE_API_KEY" not in os.environ:
            error(
                "No api key found. Pass one in via -a / --apikey or set it in OPENSTORE_API_KEY"
            )
            exit(1)

        args = ["publish"]
        if api and "OPENSTORE_API_KEY" not in os.environ:
            args += ["--apikey", api]

        build_result = run_inside_venv("clickable", args, dev_venv_path, check=False)

    if build_result.returncode != 0:
        if "No device detected" in build_result.stdout:
            error(
                "\nNo device in developer mode was found. This isn't usually the fault of clickable or TaUTus."
            )
            exit(1)
        else:
            handle_run_error(
                build_result,
                "Clickable failed to build the project. Please blame TaUTus first!",
            )

    if target == "device":
        device_result = run_inside_venv(
            "clickable", ["install"], dev_venv_path, check=False
        )

        if device_result.returncode != 0:
            if "No device detected" in device_result.stdout:
                error(
                    "\nNo device in developer mode was found. This isn't usually the fault of clickable or TaUTus."
                )
                exit(1)
            else:
                handle_run_error(
                    device_result,
                    "Clickable failed to install the project. Please blame TaUTus first!",
                )
    print(
        Style.DIM
        + "\nBe sure to report any issues related to TaUTUs at: https://github.com/tabbeddev/tautus"
    )
    exit()
