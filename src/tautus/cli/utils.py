from tautus.cli.colors import Fore, Style
from tautus.vars import TAUTUS_VERSION


def log(message: str):
    print(Fore.GREEN + Style.BRIGHT + message + Style.RESET_ALL)


def sublog(message: str):
    print(Fore.GREEN + message + Style.RESET_ALL)


def error(message: str):
    print(Fore.RED + message + Style.RESET_ALL)


def print_version():
    print(Fore.BLUE + "TaUTus " + Style.BRIGHT + TAUTUS_VERSION + Style.RESET_ALL)
