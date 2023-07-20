from cx_Freeze import Executable, setup

build_exe_options = {
    "packages": ["config", "server", "common", "db", "log"],
}

setup(
    version="0.1",
    name="AGBM Server",
    description="GeekBrains Study Project Server",
    options={"build_exe": build_exe_options},
    executables=[Executable("server.py", base="Win32GUI", target_name="server.exe")],
)
