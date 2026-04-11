import tautus.projects.dependencies.normal as d_normal
import tautus.projects.dependencies.dev as d_dev


def add(freezes: list[str], dev: bool, noadd: bool, dry_run: bool):
    if dev:
        d_dev.add(freezes, noadd, dry_run)
    else:
        d_normal.add(freezes, noadd, dry_run)


def update(package_names: list[str], dev: bool, noadd: bool, dry_run: bool):
    # package_names can be empty here!
    if dev:
        d_dev.update(package_names, noadd, dry_run)
    else:
        d_normal.update(package_names, noadd, dry_run)


def remove(package_names: list[str], dev: bool, noadd: bool, dry_run: bool):
    if dev:
        d_dev.remove(package_names, noadd, dry_run)
    else:
        d_normal.remove(package_names, noadd, dry_run)
