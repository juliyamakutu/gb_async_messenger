from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
import threading

from common import (PresenceRequest, ReceiveError, Response, recv_message,
                    send_message, log, ChatMessageRequest)
from log import client_logger as logger


@log(logger)
def make_presence_message(account_name: str, status: str) -> PresenceRequest:

    presence_request = PresenceRequest(
        action="presence",
        time=datetime.now().timestamp(),
        type="status",
        user=PresenceRequest.User(account_name=account_name, status=status),
    )
    logger.info("Presence message for user %s, status %s generated", account_name, status)
    return presence_request

def make_text_message(account_name: str, to_chat: str, message: str) -> ChatMessageRequest:
    data = {
        "time": datetime.now().timestamp(),
        "to": to_chat,
        "from": account_name,
        "message": message,
    }
    return ChatMessageRequest(**data)


def get_messages(conn: socket):
    while True:
        try:
            msg = recv_message(conn=conn)
        except ReceiveError:
            logger.warning("Invalid message received (%s)", msg)
            return
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
            logger.critical("Connection lost!")
            break
        if msg.get('action') == 'msg':
            print(f"{msg.get('from')}: {msg.get('message')}")
        elif msg.get('action') == 'presence':
            print(f"{msg.get('user', {}).get('account_name')} connected")


def send_messages(conn: socket, account_name: str):
    while True:
        message = input("Enter message: ")
        receiver = input("Enter receiver: ")
        try:
            send_message(
                conn=conn,
                message=make_text_message(
                    account_name=account_name,
                    to_chat=receiver,
                    message=message,
                ),
            )
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
            logger.critical("Connection lost!")
            break


def main(addr: str, port: int = typer.Argument(default=7777)):
    account_name = input("Enter your name: ")
    with socket(AF_INET, SOCK_STREAM) as s:
        s.connect((addr, port))
        logger.info("Sending presence request to %s:%s", addr, port)
        send_message(
            conn=s,
            message=make_presence_message(
                account_name=account_name,
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
        print("Connected to server")

        getter = threading.Thread(target=get_messages, args=(s,))
        getter.daemon = True
        getter.start()

        sender = threading.Thread(target=send_messages, args=(s, account_name))
        sender.daemon = True
        sender.start()

        while True:
            if getter.is_alive() and sender.is_alive():
                continue
            else:
                break


if __name__ == "__main__":
    typer.run(main)
