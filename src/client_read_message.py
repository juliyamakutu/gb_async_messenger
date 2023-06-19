from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError

from common import (PresenceRequest, ReceiveError, Response, recv_message,
                    send_message, log)
from log import client_logger as logger


def main(addr: str, port: int = typer.Argument(default=7777)):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
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
