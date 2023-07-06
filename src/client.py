import threading
from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer

from common import (ChatMessageRequest, ClientMeta, GetContactsRequest, Port,
                    PresenceRequest, ReceiveError, recv_message, send_message)
from log import client_logger as logger


class JimClient(metaclass=ClientMeta):
    port = Port()

    def __init__(self, addr: str, port: int, account_name: str):
        self.addr = addr
        self.port = port
        self.account_name = account_name

        self.socket = None
        self.running = True
        self._create_socket()

    def _create_socket(self) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.addr, self.port))
        logger.info(f"Connected to {self.addr}:{self.port}")
        self._send_presence_message(status=f"Online")
        self._get_contacts()

    def stop(self):
        self.running = False
        self.socket.close()

    def _make_presence_message(self, status: str) -> PresenceRequest:
        return PresenceRequest(
            action="presence",
            time=datetime.now().timestamp(),
            type="status",
            user=PresenceRequest.User(account_name=self.account_name, status=status),
        )

    def _make_get_contacts_message(self) -> GetContactsRequest:
        return GetContactsRequest(
            action="get_contacts",
            time=datetime.now().timestamp(),
            user_login=self.account_name,
        )

    def _send_presence_message(self, status: str) -> None:
        presence_message = self._make_presence_message(status=status)
        send_message(conn=self.socket, message=presence_message)
        logger.info("Presence message sent")
        msg = recv_message(conn=self.socket)
        logger.info(f"Response: {msg}")

    def _get_contacts(self) -> None:
        get_contacts_message = self._make_get_contacts_message()
        send_message(conn=self.socket, message=get_contacts_message)
        logger.info("Contacts message sent")
        while True:
            msg = recv_message(conn=self.socket)
            if msg.get("response") == 202:
                logger.info(f"Got contact list: {msg.get('alert')}")
                break

    def make_text_message(self, to_chat: str, message: str) -> ChatMessageRequest:
        data = {
            "time": datetime.now().timestamp(),
            "to": to_chat,
            "from": self.account_name,
            "message": message,
        }
        return ChatMessageRequest(**data)

    def get_messages(self):
        try:
            msg = recv_message(conn=self.socket)
            logger.info(f"Message received: {msg}")
        except ReceiveError:
            logger.warning("Invalid message received (%s)", msg)
            return
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
            logger.critical("Connection lost!")
            self.stop()
        else:
            if msg.get("action") == "msg":
                return f"{msg.get('from')}: {msg.get('message')}"
            elif msg.get("action") == "presence":
                return f"{msg.get('user', {}).get('account_name')} connected"

    def send_messages(self, message: str, receiver: str):
        try:
            send_message(
                conn=self.socket,
                message=self.make_text_message(
                    to_chat=receiver,
                    message=message,
                ),
            )
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError):
            logger.critical("Connection lost!")
            self.stop()


def get_messages(client: JimClient):
    while client.running:
        if message := client.get_messages():
            print(message)


def user_interface(client: JimClient):
    while client.running:
        message = input("Enter message: ")
        receiver = input("Enter receiver: ")
        client.send_messages(message=message, receiver=receiver)


def main(addr: str, port: int = typer.Argument(default=7777)):
    account_name = input("Enter your name: ")
    client = JimClient(addr=addr, port=port, account_name=account_name)

    getter = threading.Thread(target=get_messages, args=(client,))
    getter.daemon = True
    getter.start()

    sender = threading.Thread(target=user_interface, args=(client,))
    sender.daemon = True
    sender.start()

    while True:
        if getter.is_alive() and sender.is_alive():
            continue
        else:
            break


if __name__ == "__main__":
    typer.run(main)
