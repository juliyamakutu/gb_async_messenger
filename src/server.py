import sys
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from common import (PresenceRequest, ReceiveError, Response, recv_message,
                    send_message, log)
from config import server_config as config
from log import server_logger as logger


@log(logger)
def parse_message(msg: dict) -> Response:
    msg_action = msg.get("action")
    if msg_action == "presence":
        try:
            PresenceRequest(**msg)
        except ValidationError:
            logger.warning("Invalid presence message: %s", msg)
            return Response(response=400, alert="Bad Request")
        logger.info("Presence message received from user %s", msg["user"]["account_name"])
        return Response(response=200, alert="OK")
    else:
        logger.warning("Unknown message type: %s", msg_action)
        return Response(response=400, alert="Bad Request")


def main(
    host: Annotated[str, typer.Option("-a")] = config.host,
    port: Annotated[int, typer.Option("-p")] = config.port,
):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    s.listen(config.max_connections)
    logger.info("Server started on %s:%s", host, port)
    try:
        while True:
            conn, addr = s.accept()
            with conn:
                logger.info(f"Connected by %s", addr)
                try:
                    msg = recv_message(conn=conn)
                except ReceiveError:
                    logger.warning("Invalid message received (%s)", msg)
                    conn.close()
                    continue
                response = parse_message(msg=msg)
                send_message(conn=conn, message=response)
                conn.close()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        s.close()
        sys.exit()
    finally:
        logger.info("Server stopped")
        s.close()


if __name__ == "__main__":
    typer.run(main)
