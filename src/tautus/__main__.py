import os
from tautus.commands.init import init
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

    if args.command == "init":
        init(args)
    elif args.command == "version":
        print_version()
    else:
        content = os.listdir(".")

        if "tautus.json" not in content or "tautus-venv" not in content:
            error(
                "This command needs to be run inside a TaUTus project. Create one with ./tautus.pyz init"
            )
            exit(1)
        else:
            error("I'm sorry, but that command hasn't been implemented yet.")
            exit(1)
