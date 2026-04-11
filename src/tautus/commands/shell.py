import os
import subprocess

from tautus.projects.dependencies.normal import install_all_deps
from tautus.utils import handle_run_error
from tautus.vars import INSTALLED_LIBS_PATH, VENV_PATH


def shell(command: str | None):
    venv_path = VENV_PATH.absolute()
    venv_python = venv_path / "bin" / "python"

    env = os.environ.copy()

    python_libs = install_all_deps(os.uname().machine)

    if "PYTHONPATH" not in env:
        env["PYTHONPATH"] = ""

    env["PYTHONPATH"] += ":" + str(python_libs.absolute())

    args = [venv_python]
    if command:
        args += ["-c", command]

    result = subprocess.run(args, text=True, env=env)

    handle_run_error(result, "The called python instance exited with an error")
