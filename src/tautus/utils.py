import os
import subprocess
from pathlib import Path
from importlib.resources import files

from tautus.cli.colors import Fore, Style
from tautus.cli.utils import error, sublog


def run_inside_venv(
    command: str,
    args: list[str],
    venv_path: os.PathLike,
    capture_output: bool = True,
    log_output: bool = True,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    venv_path = Path(venv_path)

    venv_env = os.environ.copy()
    venv_env["VIRTUAL_ENV"] = str(venv_path.absolute)
    venv_env["PATH"] = f"{venv_env['VIRTUAL_ENV']}/bin:" + venv_env["PATH"]

    absolute_path = (venv_path / "bin" / command).absolute()
    command_path = str(absolute_path)

    p = subprocess.Popen(
        [command_path, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    lines: list[str] = []

    for line in p.stdout:  # pyright: ignore[reportOptionalIterable]
        if log_output:
            print(line, end="")
        lines.append(line)

    p.wait()
    stdout = "".join(lines)
    if p.returncode != 0 and check:
        raise subprocess.CalledProcessError(p.returncode, p.args)
    elif capture_output:
        return subprocess.CompletedProcess(p.args, p.returncode, stdout)
    else:
        return subprocess.CompletedProcess(p.args, p.returncode)


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


def handle_run_error(process: subprocess.CompletedProcess[str], error_msg: str):
    if process.returncode == 0:
        return

    print(
        Fore.RED
        + Style.BRIGHT
        + f"A process started by TaUTus exited with error code {process.returncode}:"
        + Style.RESET_ALL
    )
    error(error_msg)

    if process.stdout:
        print(Fore.BLUE + Style.BRIGHT + "\n---- STDOUT ----\n" + Style.RESET_ALL)

        for index, line in enumerate(process.stdout.strip().splitlines()):
            print(f"{Style.DIM}{index + 1}: {Style.NORMAL}{line}")

    print(Fore.BLUE + Style.BRIGHT + "\n----  ARGS  ----\n" + Style.RESET_ALL)

    for index, arg in enumerate(process.args):
        print(f"{Style.DIM}{index + 1}: {Style.NORMAL}{arg}")

    print(Fore.BLUE + Style.BRIGHT + "\n----------------\n" + Style.RESET_ALL)
    print(
        Fore.YELLOW
        + "If you think this issue is related to TaUTus, report it here: https://github.com/tabbeddev/tautus"
    )
    exit(process.returncode)
