import os

import tautus.commands.init as c_init
import tautus.commands.build as c_build
import tautus.commands.dependencies as c_dependencies
import tautus.commands.shell as c_shell
from tautus.cli.argparse import parse_args
from tautus.cli.utils import error, print_version


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
    elif not is_installed_project and args.command != "install":
        error(
            "You need to install all dependencies from this TaUTus project first. Do that with ./tautus.pyz install"
        )
        exit(1)

    # Build project
    elif args.command == "build":
        c_build.build(args.target, args.apikey)

    # Dependency management
    elif args.command == "deps":
        if args.deps_action == "add":
            c_dependencies.add(args.name, args.dev, args.noadd)
        elif args.deps_action == "update":
            c_dependencies.update(args.name, args.dev, args.noadd)
        else:
            c_dependencies.remove(args.name, args.dev, args.noadd)

    # Open python shell inside project
    elif args.command == "shell":
        c_shell.shell(args.shell_command)

    else:
        error("I'm sorry, but that command hasn't been implemented yet.")
        exit(1)
