import subprocess
import typer

from typing_extensions import Annotated


def main(
        addr: str,
        port: int = typer.Argument(default=7777),
        clients_count: Annotated[int, typer.Option("-c")] = 1,
):
    PROCESSES = []

    subprocess.Popen(["python", "src/server.py", "-a", addr, "-p", str(port)], shell=True)
    for i in range(clients_count):
        client = subprocess.Popen(["python", "src/client.py", addr, str(port)], shell=True)
        PROCESSES.append(client)

    input("Press Enter to exit\n")

    for process in PROCESSES:
        process.kill()


if __name__ == "__main__":
    typer.run(main)
