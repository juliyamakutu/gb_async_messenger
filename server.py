import json
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from jim_types import PresenceRequest, Response


def main(
    host: Annotated[str, typer.Option("-a")] = "",
    port: Annotated[int, typer.Option("-p")] = 7777,
):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    s.listen(5)
    print("Server started")
    try:
        while True:
            conn, addr = s.accept()
            with conn:
                print("Connected by", addr)
                data = conn.recv(4096)
                try:
                    request = PresenceRequest(
                        **json.loads(data.decode(encoding="utf-8"))
                    )
                except (json.JSONDecodeError, ValidationError):
                    print("Invalid data")
                    conn.close()
                    continue
                print(f"Received '{request.action}' command")
                response = Response(response=200, alert="OK")
                conn.send(response.json().encode(encoding="utf-8"))
                conn.close()
    finally:
        print("Server stopped")
        s.close()


if __name__ == "__main__":
    typer.run(main)
