import re
from os import PathLike
from tautus.projects.project_parser import ProjectManifest
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
    args = ["-m", "pip", "list", "--format=freeze"]

    if not dev:
        args.append("--path=python-libs")

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
