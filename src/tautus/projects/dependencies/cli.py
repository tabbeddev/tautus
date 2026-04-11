from tautus.cli.colors import Fore, Style


def log_installed(name: str, version: str):
    print(
        f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed: {Fore.RESET}{name}=={version}"
    )


def log_uninstalled(name: str, version: str):
    print(
        f"{Fore.GREEN}{Style.BRIGHT}[-]{Style.NORMAL} Uninstalled: {Fore.RESET}{name}=={version}"
    )


def log_added_manifest(name: str, version: str):
    print(
        f"{Fore.CYAN}{Style.BRIGHT}[+]{Style.NORMAL} Added to the manifest: {Fore.RESET}{name}=={version}"
    )


def log_already_installed(name: str, version: str):
    print(f"[/]{Style.DIM} Was already installed: {Style.NORMAL}{name}=={version}")


def log_already_up_to_date(name: str, version: str):
    print(
        f"{Fore.CYAN}[/]{Style.DIM} Already up-to-date: {Style.RESET_ALL}{name}=={version}"
    )


def log_not_installed(name: str):
    print(f"[/]{Style.DIM} Is not installed: {Style.NORMAL}{name}")


def log_removed_manifest(name: str, version: str):
    print(
        f"{Fore.CYAN}{Style.BRIGHT}[-]{Style.NORMAL} Was removed from the manifest: {Fore.RESET}{name}=={version}"
    )
