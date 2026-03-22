import sys
import os
import shutil
import io
import zipfile
import tempfile
import pyotherside  # pyright: ignore[reportMissingImports]

_QRC_ROOT = "/python-libs"
_EXTRACTED_PATH = None


def _extract_python_libs(target: str):
    """Extracts python libraries from the included zip file."""
    zip_content: bytearray = pyotherside.qrc_get_file_contents(
        _QRC_ROOT + "/python.zip"
    )

    with zipfile.ZipFile(io.BytesIO(zip_content)) as zip_file:
        zip_file.extractall(target)


def clean_up():
    """
    Deleted extracted python-libs.
    Causes imports from python-libs to fail.
    """
    global _EXTRACTED_PATH

    if not _EXTRACTED_PATH:
        return

    print("[tautus-libs] Cleaning up extracted libs...")
    shutil.rmtree(_EXTRACTED_PATH)

    _EXTRACTED_PATH = None


class _StdoutBridge:
    def write(self, text):
        text = str(text).strip()
        if text:
            pyotherside.send("stdout", text)

    def flush(self):
        pass


def initialise_log():
    """
    Overwrites built-in print function to make it work inside QML
    """
    sys.stdout = _StdoutBridge()
    sys.stderr = sys.stdout


def load_libs():
    """
    Make python-libs from QRC importable via sys.path.
    Safe to call multiple times.
    """
    global _EXTRACTED_PATH

    if _EXTRACTED_PATH is not None:
        return _EXTRACTED_PATH

    if not pyotherside.qrc_is_dir(_QRC_ROOT):
        print("[tautus-libs] No QRC python-libs found, skipping.")
        print(
            "[tautus-libs] If you have no libraries installed, you can safely ignore this warning."
        )
        return None

    temp_root = tempfile.mkdtemp(prefix="tautus-python-libs-")
    target = os.path.join(temp_root, "python-libs")
    os.makedirs(target, exist_ok=True)

    _extract_python_libs(target)

    sys.path.insert(0, target)
    _EXTRACTED_PATH = target

    print("[tautus-libs] Extracted libs. Have a good day!")
    pyotherside.atexit(clean_up)

    return target
