from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer

from common import (PresenceRequest, ReceiveError, recv_message,
                    send_message)
from log import client_logger as logger


def presence_message() -> PresenceRequest:
    presence_request = PresenceRequest(
        action="presence",
        time=datetime.now().timestamp(),
        type="status",
        user=PresenceRequest.User(account_name="Reader", status="Yep, I am here!"),
    )
    logger.info("Presence message for user %s, status %s generated", "Guest", "Yep, I am here!")
    return presence_request


def main(addr: str, port: int = typer.Argument(default=7777)):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
        send_message(conn=s, message=presence_message())
        while True:
            try:
                msg = recv_message(conn=s)
                if msg and msg.get('action') == 'msg':
                    print(f"{msg.get('from')}: {msg.get('message')}")
            except ReceiveError:
                logger.warning("Invalid message received (%s)", msg)
                s.close()
                return


if __name__ == "__main__":
    typer.run(main)
