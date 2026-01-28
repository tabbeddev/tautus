import os
import subprocess
from pathlib import Path


def run_inside_venv(
    command: str, args: list[str], venv_path: Path, capture_output: bool = False
):
    venv_env = os.environ.copy()
    venv_env["VIRTUAL_ENV"] = str(venv_path.absolute)
    venv_env["PATH"] = f"{venv_env['VIRTUAL_ENV']}/bin:" + venv_env["PATH"]

    absolute_path = (venv_path / "bin" / command).absolute()
    command_path = str(absolute_path)

    return subprocess.run(
        [command_path, *args], check=True, env=venv_env, capture_output=capture_output
    )


def get_tmp_path() -> Path:
    pid = os.getpid()
    path = "/tmp/" + str(pid)
    os.makedirs(path, exist_ok=True)

    return Path(path)
