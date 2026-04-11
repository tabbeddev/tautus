import tautus.projects.dependencies.cli as cli
from tautus.cli.utils import drylog, error
from tautus.cli.colors import Fore, Style
from tautus.projects.dependencies.utils import (
    find_requested_version,
    get_installed_list,
    understand_pip_output,
    handle_pip_output,
)
from tautus.projects.project_parser import (
    check_if_extended,
    dump_project_json,
    parse_project_json,
)
from tautus.utils import run_inside_venv, handle_run_error
from tautus.vars import VENV_PATH


def _install(freezes: list[str], dry_run: bool = False, update: bool = False):
    args = [
        "-m",
        "pip",
        "install",
        *freezes,
    ]
    if update:
        args.insert(3, "--upgrade-strategy=only-if-needed")
        args.insert(3, "--upgrade")

    if dry_run:
        drylog(f'Execute "python {" ".join(args)}" inside venv')
        return ""
    else:
        result = run_inside_venv(
            "python",
            args,
            check=False,
            log_output=False,
        )
        handle_run_error(result, "Pip failed to install dependencies")
        return result.stdout


def install_all_deps():
    manifest = parse_project_json()

    output = _install(manifest["dev_requirements"])

    print(
        f"{Fore.GREEN}{Style.BRIGHT}[+]{Style.NORMAL} Installed all dev dependencies{Style.RESET_ALL}"
    )


def add(freezes: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    pip_freezes: list[str] = []
    packages: list[str] = []

    for freeze in freezes:
        _split_name = freeze.rsplit("==", 1)
        package_name = _split_name[0]
        package_version = _split_name[1] if len(_split_name) > 1 else None

        manifest_version = find_requested_version(package_name, True, manifest)

        requested_version = package_version or manifest_version

        if requested_version and manifest_version == requested_version:
            cli.log_already_installed(package_name, requested_version)
            continue

        if requested_version:
            pip_freezes.append(package_name + "==" + requested_version)
        else:
            pip_freezes.append(package_name)
        packages.append(package_name)

    if len(pip_freezes) == 0:
        return

    output = _install(pip_freezes, dry_run)
    actions = understand_pip_output(output)

    handle_pip_output(actions, packages, manifest, noadd or dry_run, True)

    if not (noadd or dry_run):
        dump_project_json(".", manifest)


def remove(package_names: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    for package in package_names:
        requested_version = find_requested_version(package, True, manifest)

        if not requested_version:
            package_names.remove(package)
            cli.log_not_installed(package)

    if len(package_names) == 0:
        return

    args = ["-m", "pip", "uninstall", "-y", *package_names]

    if dry_run:
        drylog(f'Execute "python {" ".join(args)}"')
    else:
        result = run_inside_venv(
            "python", args, capture_output=True, log_output=False, check=False
        )

        handle_run_error(result, "Pip failed to uninstall the packages")

        actions = understand_pip_output(result.stdout)

        handle_pip_output(actions, package_names, manifest, noadd or dry_run, True)

    if not (noadd or dry_run):
        dump_project_json(".", manifest)


def update(package_names: list[str], noadd: bool, dry_run: bool = False):
    manifest = parse_project_json()
    check_if_extended(manifest)

    pre_installed_list = get_installed_list(VENV_PATH, True)

    if len(package_names) == 0:
        # When no packages are specified, update all
        package_names = [req.rsplit("==", 1)[0] for req in manifest["dev_requirements"]]

    if len(package_names) == 0:
        error("There is nothing to update")
        exit(1)

    output = _install(package_names, dry_run, True)
    actions = understand_pip_output(output, pre_installed_list)

    handle_pip_output(actions, package_names, manifest, noadd, True, True)

    if not (noadd or dry_run):
        dump_project_json(".", manifest)
