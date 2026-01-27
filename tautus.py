#!/usr/bin/python3
import argparse
import venv
import os
import subprocess
import re
import shutil
import json
from datetime import datetime
from pathlib import Path
from colorama import Fore, Style

TAUTUS_VERSION = "dev"
VALID_LICENSES = ["gpl3", "mit", "bsd", "isc", "apache", "proprietary"]


def log(message: str):
    print(Fore.GREEN + Style.BRIGHT + message + Style.RESET_ALL)


def error(message: str):
    print(Fore.RED + message + Fore.RESET)


def run_inside_venv(
    command: str, args: list[str], venv_path: Path, capture_output: bool = False
):
    venv_env = os.environ.copy()
    venv_env["VIRTUAL_ENV"] = str(venv_path.absolute)
    venv_env["PATH"] = f"{venv_env['VIRTUAL_ENV']}/bin:" + venv_env["PATH"]

    absolute_path = (venv_path / "bin" / command).absolute()
    command_path = str(absolute_path)

    return subprocess.run(
        [command_path, *args], check=True, env=venv_env, capture_output=capture_output
    )


def get_tmp_path() -> Path:
    pid = os.getpid()
    path = "/tmp/" + str(pid)
    os.makedirs(path, exist_ok=True)

    return Path(path)


def init(
    title: str,
    name: str,
    namespace: str,
    description: str,
    maintainer: str,
    mail: str,
    license: str,
    dirname: str,
    basic: bool,
    clickable_version: str | None,
):
    if not dirname:
        dirname = "."

    os.makedirs(dirname, exist_ok=True)
    content = os.listdir(dirname)
    if "tautus.py" in content:
        content.remove("tautus.py")

    absolute_path = Path(dirname).absolute()

    if len(content) != 0:
        error(
            f"The target directory ({absolute_path}) isn't empty. Please check if you specified the right directory and if so empty it. (The file tautus.py is ignored)"
        )
        exit(1)

    # Create venv

    log("Creating venv...")

    venv_path = absolute_path / "tautus-venv"

    venv.create(
        env_dir=str(venv_path), prompt="Tautus: " + title, symlinks=True, with_pip=True
    )

    venv_python = venv_path / "bin" / "python"

    log("Upgrading pip")

    subprocess.run(
        [venv_python, "-m", "pip", "install", "--upgrade", "pip"], check=True
    )

    if clickable_version:
        log("Installing clickable " + clickable_version)

        subprocess.run(
            [venv_python, "-m", "pip", "install", "clickable-ut==" + clickable_version],
            check=True,
        )
    else:
        log("Installing latest clickable")

        subprocess.run(
            [venv_python, "-m", "pip", "install", "clickable-ut"], check=True
        )

    if not clickable_version:
        log("Testing clickable")

        version_result = run_inside_venv(
            "clickable", ["--version"], venv_path, capture_output=True
        )
        version_text = version_result.stderr.decode()
        print(version_text, end="")

        version_match = re.search(
            r"clickable (\d\.\d\.\d)", version_text, re.IGNORECASE
        )
        if not version_match:
            error(
                "Clickable Test failed: Version pattern wasn't found! TaUTus can't continue."
            )
            exit(1)

        clickable_version = version_match.group(1)

    tmp_path = get_tmp_path()

    log("Creating clickable project")

    run_inside_venv(
        "clickable",
        [
            "create",
            "--title",
            title,
            "--name",
            name,
            "--namespace",
            namespace,
            "--description",
            description,
            "--maintainer",
            maintainer,
            "--mail",
            mail,
            "--license",
            license,
            "--template",
            "python-cmake",
            "--non-interactive",
            "--dir",
            str(tmp_path),
        ],
        venv_path,
        capture_output=True,  # I don't care about the output, but I also don't want it to tell some invalid path
    )

    tmp_clickable_path = (tmp_path / name).absolute()
    if not tmp_clickable_path.exists():
        error("The created clickable project was not found! TaUTus can't continue.")
        exit(1)

    log("Completing...")

    shutil.copytree(tmp_clickable_path, absolute_path, dirs_exist_ok=True)
    shutil.copy("./tautus.py", absolute_path)
    shutil.rmtree(tmp_clickable_path)

    os.makedirs(absolute_path / "python-libs", exist_ok=True)

    tautus_json = {
        "clickable-version": clickable_version,
        "metadata": {
            "title": title,
            "name": name,
            "namespace": namespace,
            "description": description,
            "maintainer": maintainer,
            "mail": mail,
            "license": license,
            "copyright-year": str(datetime.today().year),
            "version": "0.0.1",
        },
        "requirements": [],
        "dev-requirements": [],
        "pre-build-commands": [],
        "pre-release-build-commands": [],
    }

    with open(absolute_path / "tautus.json", "w") as file:
        json.dump(tautus_json, file, indent=4)

    if basic:
        log("Skip merging project with TaUTus project")
    else:
        log("Merge project with TaUTus project")

        # TODO: Implement template system

    print(
        Fore.BLUE
        + Style.BRIGHT
        + "\nYour TaUTus app is now ready to go at the directory: "
        + Style.RESET_ALL
        + str(absolute_path)
    )
    print(
        Style.DIM
        + "Be sure to report any issues at: https://github.com/tabbeddev/tautus"
    )
    exit()


def init_cli(args: argparse.Namespace):
    def ask_value(question: str, default: str) -> str:
        answer = ""

        while answer == "":
            answer = input(
                f"{Fore.BLUE}{Style.BRIGHT}{question} {Style.RESET_ALL}(e.g. {Fore.GREEN}{default}{Fore.RESET}){Fore.YELLOW} "
            ).strip()

        return answer

    dirname: str = args.dirname or "."
    title: str | None = args.title
    name: str | None = args.name
    namespace: str | None = args.namespace
    description: str | None = args.description
    maintainer: str | None = args.maintainer
    mail: str | None = args.mail
    license: str | None = args.license
    clickable_version: str | None = args.clickable_version
    basic: bool = args.basic

    if not title:
        title = ask_value("What should your app be called?", "appname")
    if not name:
        name = ask_value("What should be the name of your app?", "App Name")
    if not description:
        description = ask_value(
            "Describe shortly what your app is", "A short Hello, World! example"
        )
    if not namespace:
        namespace = ask_value(
            "What is your or the name of your organization?", "developer"
        )
    if not maintainer:
        maintainer = ask_value(
            "What name has the person maintaining it?", "Your Full Name"
        )
    if not mail:
        mail = ask_value("Enter a e-mail address of the maintainer", "email@domain.org")

    if license not in VALID_LICENSES:
        print(Style.RESET_ALL + "\nProject Licenses:")
        for licence in VALID_LICENSES:
            print(f"- {Fore.CYAN}{licence}{Fore.RESET}")

    while license not in VALID_LICENSES:
        license = input(
            f"{Fore.BLUE}{Style.BRIGHT}Please choose a licence:{Fore.YELLOW}{Style.NORMAL} "
        )

    return init(
        title,
        name,
        namespace,
        description,
        maintainer,
        mail,
        license,
        dirname,
        basic,
        clickable_version,
    )


def parse_args():
    parser = argparse.ArgumentParser(
        prog="./tautus.py",
        description="TaUTus - All in one tool for Python Ubuntu Touch Apps",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

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


def main():
    if not os.path.exists("./tautus.py"):
        error(
            'The current directory does not contain "tautus.py". Please change to the correct directory or rename the file back.'
        )
        exit(1)

    args = parse_args()

    if args.command == "init":
        init_cli(args)
    elif args.command == "version":
        print(Fore.BLUE + "TaUTus " + Style.BRIGHT + TAUTUS_VERSION + Style.RESET_ALL)
        exit()
    else:
        content = os.listdir(".")
        if "tautus.json" not in content or "tautus-venv" not in content:
            error(
                "This command needs to be run inside a TaUTus project. Create one with ./tautus.py init"
            )
            exit(1)
        else:
            error("I'm sorry, but that command hasn't been implemented yet.")
            exit(1)


if __name__ == "__main__":
    main()
