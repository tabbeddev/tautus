import os
import re
import typing
from os import PathLike
import tautus.projects.dependencies.cli as cli
from tautus.projects.types import ProjectManifest
from tautus.utils import handle_run_error, run_inside_venv


def find_requested_version(
    name: str, dev: bool, manifest: ProjectManifest
) -> str | None:
    requirements = manifest["dev_requirements" if dev else "requirements"]
    find_pattern = rf"{name}==(\S*)"

    for requirement in requirements:
        match = re.match(find_pattern, requirement)
        if match:
            return match.group(1)


def find_installed_version(name: str, installed_list: dict[str, str]):
    if name in installed_list:
        return installed_list[name]


def get_installed_list(venv_path: PathLike | str, dev: bool):
    args = ["-m", "pip", "list", "--local", "--format=freeze"]

    if not dev:
        args.append("--path=.tautus/python-libs/" + os.uname().machine)

    results = run_inside_venv("python", args, venv_path, log_output=False, check=False)

    handle_run_error(results, "Pip failed to list already installed packages")

    return dict(l.split("==") for l in results.stdout.splitlines())


def add_dependency_to_manifest(
    manifest: ProjectManifest, dev: bool, name: str, version: str
):
    remove_dependency_from_manifest(manifest, dev, name)

    requirements = manifest["dev_requirements" if dev else "requirements"]
    requirements.append(name + "==" + version)


def remove_dependency_from_manifest(manifest: ProjectManifest, dev: bool, name: str):
    requirements = manifest["dev_requirements" if dev else "requirements"]

    for req in requirements:
        if req.startswith(name + "=="):
            requirements.remove(req)


class PipUnderstanding(typing.TypedDict):
    name: str
    version: str
    action: typing.Literal[
        "installed", "uninstalled", "already-installed", "already-uninstalled"
    ]


def understand_pip_output(
    output: str, pre_installed_list: dict[str, str] | None = None
):
    results: list[PipUnderstanding] = []

    for line in output.splitlines():
        line = line.strip()
        if line.startswith("Successfully installed "):
            for package in line.removeprefix("Successfully installed ").split():
                name, version = package.rsplit("-", 1)

                if pre_installed_list and pre_installed_list[name] == version:
                    results.append(
                        {
                            "name": name,
                            "version": version,
                            "action": "already-installed",
                        }
                    )
                else:
                    results.append(
                        {"name": name, "version": version, "action": "installed"}
                    )
        elif line.startswith("Successfully uninstalled "):
            name, version = line.removeprefix("Successfully uninstalled ").rsplit(
                "-", 1
            )
            results.append({"name": name, "version": version, "action": "uninstalled"})
        elif line.startswith("WARNING: Target directory"):
            folder = (
                line.removeprefix("WARNING: Target directory ")
                .split(" already exists")[0]
                .rsplit("/", 1)[1]
            )
            if not folder.endswith(".dist-info"):
                continue

            name, version = folder.removesuffix(".dist-info").split("-")

            results.append(
                {"name": name, "version": version, "action": "already-installed"}
            )
            for result in results:
                if result["action"] == "installed" and result["name"] == name:
                    results.remove(result)
        elif line.startswith("WARNING: Skipping"):
            match = re.match(r"WARNING: Skipping (\S*) as it is not installed.", line)
            if not match:
                continue

            results.append(
                {"name": match.group(1), "version": "", "action": "already-uninstalled"}
            )
        elif line.startswith("Requirement already satisfied:"):
            match = re.match(
                r"Requirement already satisfied: (\S*) in [^\(]*\(([^\)]*)\)", line
            )
            if not match:
                continue

            name, version = match.groups()
            results.append(
                {"name": name, "version": version, "action": "already-installed"}
            )

    return results


def handle_pip_output(
    actions: list[PipUnderstanding],
    explicit_packages: list[str],
    manifest: ProjectManifest,
    noadd: bool,
    dev: bool,
    update_mode: bool = False,
):
    for action in actions:
        if action["name"] in explicit_packages:
            manifest_version = find_requested_version(action["name"], dev, manifest)

            if action["action"] == "installed":
                cli.log_installed(action["name"], action["version"])
            elif action["action"] == "uninstalled":
                cli.log_uninstalled(action["name"], action["version"])
            elif action["action"] == "already-installed":
                if update_mode:
                    cli.log_already_up_to_date(action["name"], action["version"])
                else:
                    cli.log_already_installed(action["name"], action["version"])
            elif action["action"] == "already-uninstalled":
                cli.log_not_installed(action["name"])

            if not noadd:
                if manifest_version != action["version"] and (
                    action["action"] == "installed"
                    or action["action"] == "already-installed"
                ):
                    cli.log_added_manifest(action["name"], action["version"])
                    add_dependency_to_manifest(
                        manifest, dev, action["name"], action["version"]
                    )
                elif manifest_version and (
                    action["action"] == "uninstalled"
                    or action["action"] == "already-uninstalled"
                ):
                    cli.log_removed_manifest(action["name"], action["version"])
                    remove_dependency_from_manifest(manifest, dev, action["name"])
