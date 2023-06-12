import json
from socket import socket

from config import base_config as config

from .exceptions import ReceiveError
from .jim_types import Request, Response


def send_message(conn: socket, message: Request | Response) -> None:
    conn.send(message.json().encode(encoding=config.encoding))


def recv_message(conn: socket) -> dict:
    msg_bytes = conn.recv(config.bytes_to_recv)
    try:
        return json.loads(msg_bytes.decode(encoding=config.encoding))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ReceiveError
