import os
from pathlib import Path

import tautus.commands.init as c_init
import tautus.commands.install as c_install
import tautus.commands.info as c_info
import tautus.commands.build as c_build
import tautus.commands.dependencies as c_dependencies
import tautus.commands.shell as c_shell
import tautus.commands.convert as c_convert
from tautus.cli.argparse import parse_args
from tautus.cli.utils import error, print_version
from tautus.utils import run_inside_venv


def main():
    # Check if tautus.pyz exists.
    # Needed for copying into new projects
    if not os.path.exists("tautus.pyz"):
        error(
            "tautus.pyz wasn't found. Please change to the correct directory or download the latest tautus.pyz file"
        )
        exit(1)

    args = parse_args()

    content = os.listdir(".")
    is_project = "tautus.json" in content
    is_installed_project = is_project and "tautus-venv" in content

    # Initialise project
    if args.command == "init":
        c_init.init(args)

    # Print version
    elif args.command == "version":
        print_version()

    # Check if command requires a project
    elif not is_project and args.command not in ["init", "version"]:
        error(
            "This command needs to be run inside a TaUTus project. Create one with ./tautus.pyz init"
        )
        exit(1)

    # Check if command requires a project with installed dependencies
    elif not is_installed_project and args.command not in ["install", "info"]:
        error(
            "You need to install all dependencies from this TaUTus project first. Do that with ./tautus.pyz install"
        )
        exit(1)

    # Convert a project to a TaUTus extended one
    elif args.command == "convert":
        c_convert.extend(args.force)

    # Build project
    elif args.command == "build":
        c_build.build(args.target, args.apikey)

    # Dependency management
    elif args.command == "deps":
        if args.deps_action == "add":
            c_dependencies.add(
                args.name,
                args.dev,
                args.noadd,
                args.dry_run,
                args.ignore_compatability,
            )
        elif args.deps_action == "update":
            c_dependencies.update(
                args.name,
                args.dev,
                args.noadd,
                args.dry_run,
                args.ignore_compatability,
            )
        else:
            c_dependencies.remove(
                args.name, args.dev, args.noadd, args.dry_run
            )

    # Install all dependencies
    elif args.command == "install":
        c_install.install(args.dry_run, args.ignore_compatability)

    # Open python shell inside project
    elif args.command == "shell":
        c_shell.shell(args.shell_command)

    elif args.command == "ide":
        dev_venv_path = Path("tautus-venv")
        run_inside_venv(
            "clickable",
            ["ide"],
            dev_venv_path,
            capture_output=False,
            check=False,
        )

    elif args.command == "info":
        c_info.info()

    else:
        error("I'm sorry, but that command hasn't been implemented yet.")
        exit(1)
