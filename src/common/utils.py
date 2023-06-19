import json
import sys
from socket import socket

from config import base_config as config
from log import server_logger, client_logger
from .decorators import log

from .exceptions import ReceiveError
from .jim_types import Request, Response

if 'server' in sys.argv[0]:
    logger = server_logger
else:
    logger = client_logger


# @log(logger)
def send_message(conn: socket, message: Request | Response) -> None:
    conn.send(message.json(by_alias=True).encode(encoding=config.encoding))


# @log(logger)
def recv_message(conn: socket) -> dict | None:
    msg_bytes = conn.recv(config.bytes_to_recv)
    if len(msg_bytes) == 0:
        return None
    try:
        return json.loads(msg_bytes.decode(encoding=config.encoding))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ReceiveError
