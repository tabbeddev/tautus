from tautus.projects.project_parser import parse_project_json
from tautus.cli.colors import Fore, Style


def info():
    manifest = parse_project_json()
    print(Style.BRIGHT + f"{Fore.GREEN}Project Name:        {Style.RESET_ALL}{manifest['metadata']['name']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project Namespace:   {Style.RESET_ALL}{manifest['metadata']['namespace']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project Title        {Style.RESET_ALL}{manifest['metadata']['title']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project Description: {Style.RESET_ALL}{manifest['metadata']['description']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project Namespace:   {Style.RESET_ALL}{manifest['metadata']['namespace']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project License:     {Style.RESET_ALL}{manifest['metadata']['license']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project Maintainer:  {Style.RESET_ALL}{manifest['metadata']['maintainer']}")
    print(Style.BRIGHT + f"{Fore.GREEN}Project Mail:        {Style.RESET_ALL}{manifest['metadata']['mail']}")
    print()
    print(Style.BRIGHT + f"{Fore.BLUE}Project Type:      {Style.RESET_ALL}{'TaUTus extended project' if manifest["tautus_extended"]['is_extended'] else "TaUTus project"}")
    print(Style.BRIGHT + f"{Fore.BLUE}Project Version:   {Style.RESET_ALL}{manifest['metadata']['version']}")
    print(Style.BRIGHT + f"{Fore.BLUE}Project Copyright: {Style.RESET_ALL}{manifest['metadata']['copyright_year']}")
    print(Style.BRIGHT + f"{Fore.BLUE}Clickable Version: {Style.RESET_ALL}{manifest['clickable_version']}")
    print()
    print(Style.BRIGHT + Fore.YELLOW + "Requirements:" + Style.RESET_ALL)
    if not manifest["tautus_extended"]["is_extended"]:
        print("  Project not extended")
    else:
        if len(manifest["requirements"]) > 0:
            for req in manifest["requirements"]:
                print("- " + req)
        else:
            print("  No requirements added")
    print()
    print(Style.BRIGHT + Fore.YELLOW + "Dev Requirements:" + Style.RESET_ALL)
    if not manifest["tautus_extended"]["is_extended"]:
        print("  Project not extended")
    else:
        if len(manifest["dev_requirements"]) > 0:
            for req in manifest["dev_requirements"]:
                print("- " + req)
        else:
            print("  No requirements added")