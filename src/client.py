from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError

from common import (PresenceRequest, ReceiveError, Response, recv_message,
                    send_message)
from log import client_logger as logger


def make_presence_message(account_name: str, status: str) -> PresenceRequest:

    presence_request = PresenceRequest(
        action="presence",
        time=datetime.now().timestamp(),
        type="status",
        user=PresenceRequest.User(account_name=account_name, status=status),
    )
    logger.info("Presence message for user %s, status %s generated", account_name, status)
    return presence_request


def main(addr: str, port: int = typer.Argument(default=7777)):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
        logger.info("Sending presence request to %s:%s", addr, port)
        send_message(
            conn=s,
            message=make_presence_message(
                account_name="Guest",
                status="Yep, I am here!",
            )
        )
        try:
            msg = recv_message(conn=s)
            response = Response(**msg)
        except (ReceiveError, ValidationError):
            logger.warning("Invalid message received (%s)", msg)
            s.close()
            return
        logger.info("Response code %d with message '%s'", response.response, response.alert)


if __name__ == "__main__":
    typer.run(main)
