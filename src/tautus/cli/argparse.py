import argparse

from tautus.vars import VALID_LICENSES


def parse_args():
    parser = argparse.ArgumentParser(
        prog="./tautus.py",
        description="TaUTus - All in one tool for Python Ubuntu Touch Apps",
        suggest_on_error=True,
    )
    subparsers = parser.add_subparsers(dest="command", required=True, title="commands")

    # ------------------------------------------------------------------
    # init
    # ./tautus.py init [metadata args]
    # ------------------------------------------------------------------
    init_parser = subparsers.add_parser("init", help="Initialize a new UT app")
    init_parser.add_argument(
        "dirname",
        nargs="?",
        help="Target directory (defaults to current directory)",
    )
    init_parser.add_argument("--title", help="The app title as displayed to the user")
    init_parser.add_argument(
        "--name", help="Set the app name which is used in the manifest"
    )
    init_parser.add_argument(
        "--namespace", help="Namespace of the author which is used in the manifest"
    )
    init_parser.add_argument(
        "--description", help="App description which is used in the manifest"
    )
    init_parser.add_argument(
        "--maintainer", help="Maintainer name which is used in the manifest"
    )
    init_parser.add_argument(
        "--mail", help="Maintainer e-mail which is used in the manifest"
    )
    init_parser.add_argument(
        "--license",
        help="License used in the source file",
        choices=VALID_LICENSES,
    )
    init_parser.add_argument(
        "--basic", "-b", help="Don't install TaUTus template", action="store_true"
    )
    init_parser.add_argument(
        "--clickable-version", help="Specify clickable version (uses latest as default)"
    )

    # ------------------------------------------------------------------
    # deps
    # ./tautus.py deps [--dev|-d] [--noadd] <subcommand>
    # ------------------------------------------------------------------
    deps_parser = subparsers.add_parser("deps", help="Manage Python dependencies")
    deps_parser.add_argument(
        "--dev",
        "-d",
        action="store_true",
        help="Mark dependency as development dependency",
    )
    deps_parser.add_argument(
        "--noadd",
        "-n",
        action="store_true",
        help="Do not add dependency to config file (e.g. for testing)",
    )

    deps_subparsers = deps_parser.add_subparsers(dest="deps_action", required=True)

    # deps add <name>
    deps_add = deps_subparsers.add_parser("add", help="Add a dependency")
    deps_add.add_argument("name", help="Dependency name")

    # deps update [name]
    deps_update = deps_subparsers.add_parser("update", help="Update dependencies")
    deps_update.add_argument(
        "name", nargs="?", help="Optional dependency name (update all if omitted)"
    )

    # deps remove <name>
    deps_remove = deps_subparsers.add_parser("remove", help="Remove a dependency")
    deps_remove.add_argument("name", help="Dependency name")

    # ------------------------------------------------------------------
    # install
    # ./tautus.py install
    # ------------------------------------------------------------------
    subparsers.add_parser("install", help="Install all dependencies")

    # ------------------------------------------------------------------
    # build
    # ./tautus.py build <target>
    # ------------------------------------------------------------------
    build_parser = subparsers.add_parser("build", help="Build the app")
    build_parser.add_argument(
        "target", help="Build target", choices=["device", "desktop", "release"]
    )

    # ------------------------------------------------------------------
    # shell
    # ./tautus.py shell [--command|-c]
    # ------------------------------------------------------------------
    shell_parser = subparsers.add_parser("shell", help="Start a python shell")
    shell_parser.add_argument(
        "--command", "-c", help="Run this command inside the shell"
    )

    # ------------------------------------------------------------------
    # version
    # ./tautus.py version
    # ------------------------------------------------------------------
    subparsers.add_parser("version", help="Output TaUTus version")

    return parser.parse_args()
