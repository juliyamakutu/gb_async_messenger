import json
from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket
from jim_types import PresenceRequest, Response

import typer


def main(addr: str, port: int = typer.Argument(default=7777)):
    request = PresenceRequest(
        action="presence",
        time=datetime.now().timestamp(),
        type="status",
        user=PresenceRequest.User(
            account_name="Guest",
            status="Yep, I am here!"
        )
    )
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
        s.send(request.json().encode(encoding="utf-8"))
        data = s.recv(4096)
        response = Response(**json.loads(data.decode(encoding="utf-8")))
        print(f"Response code {response.response} with message '{response.alert}'")


if __name__ == "__main__":
    typer.run(main)