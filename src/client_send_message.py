from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError

from common import (
    ChatMessageRequest,
    ReceiveError,
    Response,
    log,
    recv_message,
    send_message,
)
from log import client_logger as logger


@log(logger)
def create_message(account_name: str, chat: str, message: str) -> ChatMessageRequest:
    data = {
        "time": datetime.now().timestamp(),
        "to": chat,
        "from": account_name,
        "message": message,
    }
    return ChatMessageRequest(**data)


def main(addr: str, port: int = typer.Argument(default=7777)):
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
        logger.info("Sending presence request to %s:%s", addr, port)
        send_message(
            conn=s,
            message=create_message(
                account_name="Guest",
                chat="Reader",
                message="Hello, world!",
            ),
        )
        try:
            msg = recv_message(conn=s)
            response = Response(**msg)
        except (ReceiveError, ValidationError):
            logger.warning("Invalid message received (%s)", msg)
            s.close()
            return
        logger.info(
            "Response code %d with message '%s'", response.response, response.alert
        )


if __name__ == "__main__":
    typer.run(main)
