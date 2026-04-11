import sys
import os
import pyotherside  # pyright: ignore[reportMissingImports]


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
    Make python-libs importable via sys.path.
    Safe to call multiple times.
    """
    sys.path.append(os.path.abspath("python-libs/" + os.uname().machine))
