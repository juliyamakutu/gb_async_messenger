import sys

from cx_Freeze import Executable, setup

build_exe_options = {
    "packages": ["config", "common", "db", "log", "client_gui", "client"],
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    version="0.1",
    name="AGBM Client",
    description="GeekBrains Study Project Client",
    options={"build_exe": build_exe_options},
    executables=[Executable("client/client.py", base=base, target_name="client.exe")],
)
