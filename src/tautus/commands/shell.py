import os
import subprocess
from pathlib import Path

from tautus.utils import handle_run_error


def shell(command: str | None):
    venv_path = Path("tautus-venv").absolute()
    venv_python = venv_path / "bin" / "python"

    env = os.environ.copy()

    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = ""

    env["PYTHONPATH"] += ":" + os.path.abspath("python-libs")

    args = [venv_python]
    if command:
        args += ["-c", command]

    result = subprocess.run(args, text=True, env=env)

    handle_run_error(result, "The called python instance exited with an error")
