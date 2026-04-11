import os
import typing
import json
import re
import subprocess
from pathlib import Path

from tautus.cli.utils import error, log, sublog, warn
from tautus.projects.dependencies.normal import install_all_deps
from tautus.projects.project_parser import parse_project_json
from tautus.projects.types import ProjectManifest
from tautus.utils import handle_run_error, run_inside_venv
from tautus.cli.colors import Style


def pre_build(manifest: ProjectManifest, target_arch: str):
    if (
        manifest["tautus_extended"]["qrc"]["auto_generate"]
        and manifest["tautus_extended"]["is_extended"]
    ):
        sublog("Generation QRC files...")
        for path in manifest["tautus_extended"]["qrc"]["paths"]:
            if path.startswith(("python-libs", ".tautus")):
                warn(
                    f'Path "{path}" was added in QRC paths. This path will be ignored.'
                )
                warn(
                    'To include your python libraries set "tautus_extended.include_python_libs" to true.'
                )
                continue

            directory = Path(".") / path
            qrc_target = directory / (path + ".qrc")

            discovered_paths: list[str] = []

            sublog(f"- Generating {qrc_target.name}...")

            def traverse_dir(path: Path):
                for content in path.iterdir():
                    if content.is_dir():
                        traverse_dir(content)
                    elif content.is_file():
                        if (
                            content.name == qrc_target.name
                            or str(content) == "src/main.cpp"
                        ):
                            continue

                        discovered_paths.append(str(content))

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

    if (
        manifest["tautus_extended"]["is_extended"]
        and manifest["tautus_extended"]["include_python_libs"]
    ):
        sublog(f"Installing dependencies for {target_arch}...")
        install_all_deps(target_arch)

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

    sublog("- Updating clickable.yaml")
    with open("clickable.yaml", "r+") as clickable_file:
        content = clickable_file.read()
        new_content = re.sub(
            r"(TAUTUS_ARCH: )(\w+)", r"\g<1>" + target_arch, content, 1
        )

        clickable_file.seek(0)
        clickable_file.write(new_content)
        clickable_file.truncate()


def build(
    target: typing.Literal["desktop", "device", "publish"], api: str | None = None
):
    log("Preparing build")
    manifest = parse_project_json()

    if target == "device":
        result = subprocess.run(
            ["adb", "shell", "uname", "-m"], stdout=subprocess.PIPE, text=True
        )
        target_arch = result.stdout.splitlines()[-1]
    else:
        target_arch = os.uname().machine

    sublog("Architecture: " + target_arch)

    pre_build(manifest, target_arch)

    log("Building for target: " + target.capitalize() + "\n")

    cmds = manifest["pre_build_commands"]
    if target == "publish":
        sublog("Also running pre_release commands")
        cmds += manifest["pre_release_build_commands"]

    for cmd in cmds:
        log(f'Running cmd "{cmd}":')
        result = subprocess.run(
            cmd,
            shell=True,
            text=True,
        )

        handle_run_error(result, "User specified command failed to run")
        print()

    if target == "desktop":
        build_result = run_inside_venv("clickable", ["desktop"], check=False)
    elif target == "device":
        args = ["build", "--skip-review", "--arch", "detect"]

        build_result = run_inside_venv(
            "clickable",
            args,
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

        build_result = run_inside_venv("clickable", args, check=False)

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
        device_result = run_inside_venv("clickable", ["install"], check=False)

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
