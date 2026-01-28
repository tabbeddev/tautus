#!/usr/bin/env python3
import os
import stat
import zipapp

zipapp.create_archive(
    source="src",
    target="tautus.pyz",
    main="tautus.__main__:main",
    interpreter="/usr/bin/env python3",
    compressed=True,
)
print("Create tautus.pyz")

st = os.stat("tautus.pyz")
os.chmod("tautus.pyz", st.st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
