from tautus.cli.colors import Fore, Style
from tautus.vars import TAUTUS_VERSION


def log(message: str):
    print(Fore.GREEN + Style.BRIGHT + message + Style.RESET_ALL)


def sublog(message: str):
    print(Fore.GREEN + message + Style.RESET_ALL)


def drylog(message: str):
    print(Fore.CYAN + "[dry-run] " + message + Style.RESET_ALL)


def error(message: str):
    print(Fore.RED + message + Style.RESET_ALL)


def success(message: str, message2: str):
    print(Fore.BLUE + Style.BRIGHT + message + Style.RESET_ALL + " " + message2)


def print_version():
    print(Fore.BLUE + "TaUTus " + Style.BRIGHT + TAUTUS_VERSION + Style.RESET_ALL)
