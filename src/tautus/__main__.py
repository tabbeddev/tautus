import os
import tautus.commands.init as c_init
import tautus.commands.build as c_build
from tautus.cli.argparse import parse_args
from tautus.cli.utils import log, error, print_version


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

    if args.command == "init":
        c_init.init(args)
    elif args.command == "version":
        print_version()
    elif args.command == "build" and is_project:
        c_build.build(args.target, args.apikey)
    elif not is_project and args.command not in ["init", "version"]:
        error(
            "This command needs to be run inside a TaUTus project. Create one with ./tautus.pyz init"
        )
        exit(1)
    elif not is_installed_project and args.command != "install":
        error(
            "You need to install all dependencies from this TaUTus project first. Do that with ./tautus.pyz install"
        )
        exit(1)
    else:
        error("I'm sorry, but that command hasn't been implemented yet.")
        exit(1)
