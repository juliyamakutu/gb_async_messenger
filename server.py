import logging
import sys
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from common import PresenceRequest, Response, recv_message, send_message, ReceiveError
from config import server_config as config


logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def parse_message(msg: dict) -> Response:
    msg_action = msg.get("action")
    if msg_action == "presence":
        try:
            PresenceRequest(**msg)
        except ValidationError:
            logger.warning("Invalid presence message")
            return Response(response=400, alert="Bad Request")
        return Response(response=200, alert="OK")
    else:
        logger.warning("Unknown message type")
        return Response(response=400, alert="Bad Request")


def main(
    host: Annotated[str, typer.Option("-a")] = config.host,
    port: Annotated[int, typer.Option("-p")] = config.port,
):
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    s.listen(config.max_connections)
    logger.info("Server started")
    try:
        while True:
            conn, addr = s.accept()
            with conn:
                logger.info(f"Connected by {addr}")
                try:
                    msg = recv_message(conn=conn)
                except ReceiveError:
                    logger.warning("Invalid message received")
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