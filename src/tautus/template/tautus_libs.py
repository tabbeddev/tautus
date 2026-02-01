import sys
import os
import shutil
import tempfile
import pyotherside  # pyright: ignore[reportMissingImports]

_QRC_ROOT = "/python-libs"
_EXTRACTED_PATH = None


def _extract_qrc_dir(qrc_dir: str, target_dir: str):
    """Recursively extract a QRC directory to a real filesystem path."""
    for entry in pyotherside.qrc_list_dir(qrc_dir):
        qrc_path = f"{qrc_dir}/{entry}"
        fs_path = os.path.join(target_dir, entry)

        if pyotherside.qrc_is_dir(qrc_path):
            os.makedirs(fs_path, exist_ok=True)
            _extract_qrc_dir(qrc_path, fs_path)

        elif pyotherside.qrc_is_file(qrc_path):
            data = pyotherside.qrc_get_file_contents(qrc_path)
            with open(fs_path, "wb") as f:
                f.write(data)


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

    _extract_qrc_dir(_QRC_ROOT, target)

    sys.path.insert(0, target)
    _EXTRACTED_PATH = target

    pyotherside.atexit(clean_up)

    return target
