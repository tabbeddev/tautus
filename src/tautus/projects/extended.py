import os
from pathlib import Path

from tautus.cli.utils import sublog
from tautus.utils import copy_file_from_templates, replace_text_in_file


def extend_project(name: str, namespace: str, absolute_path: Path, force: bool = False):
    sublog("Creating folders...")
    os.makedirs(absolute_path / "python-libs", exist_ok=True)
    os.makedirs(absolute_path / "qml" / "pages", exist_ok=True)
    os.makedirs(absolute_path / ".vscode", exist_ok=True)

    sublog("Copying files from TaUTus Template...")
    # Add apparmor policy
    copy_file_from_templates(
        "appname.apparmor", absolute_path / (name + ".apparmor"), force
    )

    # Add QRC files
    copy_file_from_templates(
        "assets.qrc", absolute_path / "assets" / "assets.qrc", force
    )
    copy_file_from_templates("qml.qrc", absolute_path / "qml" / "qml.qrc", force)
    copy_file_from_templates("src.qrc", absolute_path / "src" / "src.qrc", force)

    # Add C++ related stuff
    copy_file_from_templates("main.cpp", absolute_path / "src" / "main.cpp", force)
    copy_file_from_templates("CMakeLists.txt", absolute_path / "CMakeLists.txt", force)

    # Add PageStack example with Python
    copy_file_from_templates("Main.qml", absolute_path / "qml" / "Main.qml", force)
    copy_file_from_templates(
        "Home.qml", absolute_path / "qml" / "pages" / "Home.qml", force
    )

    # Add Python files
    copy_file_from_templates("main.py", absolute_path / "src" / "main.py", force)
    copy_file_from_templates(
        "tautus_libs.py", absolute_path / "src" / "tautus_libs.py", force
    )

    # Add Configs
    copy_file_from_templates(
        "settings.json", absolute_path / ".vscode" / "settings.json", force
    )
    copy_file_from_templates(
        "extensions.json", absolute_path / ".vscode" / "extensions.json", force
    )
    copy_file_from_templates("gitignore", absolute_path / ".gitignore", force)

    sublog("Modifying clickable.yaml...")
    # Set builder to plain cpp
    replace_text_in_file(
        absolute_path / "clickable.yaml",
        "builder: pure-qml-cmake",
        "builder: cmake",
        force,
    )

    sublog(f"Modifying {name}.desktop.in...")
    # Set Exec to the compiled executable
    replace_text_in_file(
        absolute_path / (name + ".desktop.in"),
        "Exec=qmlscene %U qml/Main.qml",
        "Exec=" + name,
        force,
    )

    sublog("Modifying main.cpp...")
    # Add main file
    replace_text_in_file(absolute_path / "src" / "main.cpp", "%%name%%", name, force)
    replace_text_in_file(
        absolute_path / "src" / "main.cpp", "%%namespace%%", namespace, force
    )

    sublog("Modifying CMakeLists.txt...")
    replace_text_in_file(absolute_path / "CMakeLists.txt", "%%name%%", name, force)
    replace_text_in_file(
        absolute_path / "CMakeLists.txt", "%%namespace%%", namespace, force
    )

    sublog("Modifying Main.qml..")
    replace_text_in_file(absolute_path / "qml" / "Main.qml", "%%name%%", name, force)
    replace_text_in_file(
        absolute_path / "qml" / "Main.qml", "%%namespace%%", namespace, force
    )

    sublog("Modifying snapcraft.yaml...")
    replace_text_in_file(
        absolute_path / "snapcraft.yaml",
        "command: usr/lib/qt5/bin/qmlscene $SNAP/qml/Main.qml",
        "command: " + name,
        force,
    )

    sublog("Modifying manifest.json.in...")
    replace_text_in_file(
        absolute_path / "manifest.json.in",
        '"version": "1.0.0"',
        '"version": "0.0.1"',
        force,
    )

    sublog("Deleting default Python example file...")
    # We don't need it
    os.remove(absolute_path / "src" / "example.py")
