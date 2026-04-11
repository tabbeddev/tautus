from pathlib import Path

# Increment every TaUTus release
TAUTUS_VERSION = "1.0.0"

# Increment every time the Manifest standard got an update
MANIFEST_VERSION = "1.0.0"

VENV_PATH = Path(".tautus/venv")
WHEELHOUSE_PATH = Path(".tautus/wheelhouse")
INSTALLED_LIBS_PATH = Path(".tautus/python-libs")

VALID_LICENSES = ["gpl3", "mit", "bsd", "isc", "apache", "proprietary"]
