import os
import subprocess

import typer
from typing_extensions import Annotated

PATH_TO_FILE = os.path.dirname(__file__)


def _osascript(script: str) -> subprocess.Popen:
    return subprocess.Popen(
        f'osascript -e \'tell application "Terminal" to do'
        f' script "cd {PATH_TO_FILE} && {script}"\'',
        shell=True,
    )


def main(
    addr: str,
    port: int = typer.Argument(default=7777),
    clients_count: Annotated[int, typer.Option("-c")] = 1,
):
    PROCESSES = []

    PROCESSES.append(_osascript(f"pdm run server.py -a {addr} -p {port}"))
    for i in range(clients_count):
        client = _osascript(f"pdm run client.py {addr} {port}")
        PROCESSES.append(client)

    input("Press Enter to exit\n")

    for process in PROCESSES:
        process.kill()


if __name__ == "__main__":
    typer.run(main)
