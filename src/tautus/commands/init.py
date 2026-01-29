import argparse

import tautus.cli.input_validation as val
from tautus.cli.utils import error
from tautus.projects.create_project import create_project
from tautus.vars import VALID_LICENSES
from tautus.cli.colors import Fore, Style


def init_prepare_values(args: argparse.Namespace):
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

    try:
        if not name:
            name = val.ask_value(
                "What should your app be called?",
                "appname",
                val.vp_name,
                declineMsg="The appname can only contain lowercase letters and numbers. For the title wait until the next question.",
            )
        elif not val.validate(name, val.vp_name):
            error("Validation failed: name")
            exit(1)

        if not title:
            title = val.ask_value(
                "What should be the title of your app?",
                "App Name",
                val.vp_title,
                declineMsg="For accesibility reasons stick to letters and numbers please.",
            )
        elif not val.validate(title, val.vp_title):
            error("Validation failed: title")
            exit(1)

        if not description:
            description = val.ask_value(
                "Describe shortly what your app is",
                "A short Hello, World! example",
                val.vp_description,
                declineMsg="You must specify a description",
            )
        elif not val.validate(description, val.vp_description):
            error("Validation failed: description")
            exit(1)

        if not namespace:
            namespace = val.ask_value(
                "What is your or the name of your organization?",
                "developer",
                val.vp_name,
                declineMsg="The namespace can only contain lowercase letters and numbers. For the name of the maintainer wait until the next question.",
            )
        elif not val.validate(namespace, val.vp_name):
            error("Validation failed: namespace")
            exit(1)

        if not maintainer:
            maintainer = val.ask_value(
                "What name has the person maintaining it?",
                "Your Full Name",
                val.vp_maintainer_name,
                declineMsg="You must specify a maintainer",
            )
        elif not val.validate(maintainer, val.vp_maintainer_name):
            error("Validation failed: maintainer")
            exit(1)

        if not mail:
            mail = val.ask_value(
                "Enter an e-mail address of the maintainer",
                "email@domain.org",
                val.vp_email,
                declineMsg="You must specify an e-mail address of the maintainer",
            )
        elif not val.validate(mail, val.vp_email):
            error("Validation failed: mail")
            exit(1)

        mail = mail.lower()

        if license not in VALID_LICENSES:
            print(Style.RESET_ALL + "\nProject Licenses:")
            for licence in VALID_LICENSES:
                print(f"- {Fore.CYAN}{licence}{Fore.RESET}")

        while license not in VALID_LICENSES:
            license = input(
                f"{Fore.BLUE}{Style.BRIGHT}Please choose a licence:{Fore.YELLOW}{Style.NORMAL} "
            )
    except KeyboardInterrupt:
        error("\nProject creation cancelled by user")
        exit(2)

    return (
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


def init(args: argparse.Namespace):
    values = init_prepare_values(args)

    create_project(*values)
    exit()
