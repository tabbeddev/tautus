import os
import subprocess
from pathlib import Path
from importlib.resources import files

from tautus.cli.utils import sublog


def run_inside_venv(
    command: str,
    args: list[str],
    venv_path: Path,
    capture_output: bool = False,
    check: bool = True,
):
    venv_env = os.environ.copy()
    venv_env["VIRTUAL_ENV"] = str(venv_path.absolute)
    venv_env["PATH"] = f"{venv_env['VIRTUAL_ENV']}/bin:" + venv_env["PATH"]

    absolute_path = (venv_path / "bin" / command).absolute()
    command_path = str(absolute_path)

    return subprocess.run(
        [command_path, *args], check=check, env=venv_env, capture_output=capture_output
    )


def get_tmp_path() -> Path:
    pid = os.getpid()
    path = "/tmp/" + str(pid)
    os.makedirs(path, exist_ok=True)

    return Path(path)


def copy_file_from_templates(src: str, dest: os.PathLike):
    sublog(f"- Copying {Path(dest).name} from TaUTus Template ...")

    template_files = files("tautus.template")
    content = (template_files / src).read_bytes()

    with open(dest, "wb") as file:
        file.write(content)


def replace_text_in_file(
    file_path: os.PathLike, find: str, replace: str, limit: int = -1
):
    with open(file_path, "r+") as file:
        file_content = file.read()
        new_content = file_content.replace(find, replace, limit)

        file.seek(0)
        file.write(new_content)
        file.truncate()
