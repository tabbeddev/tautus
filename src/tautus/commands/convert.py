import os
from pathlib import Path

from tautus.cli.utils import log, error, success
from tautus.cli.input_validation import confirm
from tautus.projects.project_parser import (
    check_if_not_extended,
    dump_project_json,
    parse_project_json,
)
from tautus.projects.extended import extend_project

check_msg = " This indicates this project was extended manually. Please delete it manually if you want to extend this project."


def extend():
    log("Extending project")
    manifest = parse_project_json()

    check_if_not_extended(manifest)
    if os.path.exists("python-libs"):
        error("python-libs exists." + check_msg)
        exit(1)

    if os.path.exists("tautus-venv"):
        error("tautus-venv exists." + check_msg)
        exit(1)

    answer = confirm("Do you want to extend this project?", "Y")
    if not answer:
        error("Cancelled")
        exit(1)

    name = manifest["metadata"]["name"]
    namespace = manifest["metadata"]["namespace"]
    absolute_path = Path(".").absolute()

    extend_project(name, namespace, absolute_path, False)

    success("Your project is now extended", manifest["metadata"]["title"])
