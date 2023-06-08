import json
import logging
from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError

from common import PresenceRequest, Response, recv_message, send_message, ReceiveError


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def make_presence_message(account_name: str, status: str) -> PresenceRequest:
    return PresenceRequest(
        action="presence",
        time=datetime.now().timestamp(),
        type="status",
        user=PresenceRequest.User(account_name=account_name, status=status),
    )


def main(addr: str, port: int = typer.Argument(default=7777)):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
        logger.info("Sending presence request")
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
            logger.warning("Invalid message received")
            s.close()
            return
        logger.info(f"Response code {response.response} with message '{response.alert}'")


if __name__ == "__main__":
    typer.run(main)
