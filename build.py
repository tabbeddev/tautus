#!/usr/bin/env python3
from pathlib import Path
from shutil import rmtree
import stat
import zipapp


def traverse_directory(path: Path):
    for content in path.iterdir():
        if content.is_dir():
            if content.name == "__pycache__":
                print("Deleting pycache: ", content)
                rmtree(content)
            else:
                traverse_directory(content)


traverse_directory(Path("src").absolute())

target = Path("tautus.pyz").absolute()

zipapp.create_archive(
    source="src",
    target=target,
    main="tautus.__main__:main",
    interpreter="/usr/bin/env python3",
    compressed=True,
)
print("Created", target.name)

st = target.stat()
target.chmod(st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
