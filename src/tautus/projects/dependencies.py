import re
from tautus.projects.project_parser import ProjectManifest


def find_requested_version(
    name: str, dev: bool, manifest: ProjectManifest
) -> str | None:
    requirements = manifest["dev_requirements" if dev else "requirements"]
    find_pattern = rf"{name}==(\S*)"

    for requirement in requirements:
        match = re.match(find_pattern, requirement)
        if match:
            return match.group(1)
