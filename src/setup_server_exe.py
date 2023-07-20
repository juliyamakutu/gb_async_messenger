import sys

from cx_Freeze import Executable, setup

build_exe_options = {
    "packages": ["config", "server", "common", "db", "log"],
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    version="0.1",
    name="AGBM Server",
    description="GeekBrains Study Project Server",
    options={"build_exe": build_exe_options},
    executables=[Executable("server/server.py", base=base, target_name="server.exe")],
)
