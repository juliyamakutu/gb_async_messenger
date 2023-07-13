import re
import sys
import threading
import time
from datetime import datetime
from socket import AF_INET, SOCK_STREAM, socket

import typer
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QApplication

from client_gui import ClientMainWindow, UserNameDialog
from common import (AddContactRequest, ChatMessageRequest, ClientMeta,
                    DelContactRequest, GetContactsRequest, GetUsersRequest,
                    Port, PresenceRequest, ReceiveError, recv_message,
                    send_message)
from db import ClientDatabase
from db.client_db import MessageType
from log import client_logger as logger

socket_lock = threading.Lock()


class JimClient(threading.Thread, QObject, metaclass=ClientMeta):
    port = Port()

    new_message = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(
        self, addr: str, port: int, account_name: str, storage: "ClientDatabase"
    ):
        threading.Thread.__init__(self)
        QObject.__init__(self)

        self.addr = addr
        self.port = port
        self.account_name = account_name

        self.storage = storage

        self.socket = None
        self.running = True
        self._create_socket()
        self._init_client()

    def run(self) -> None:
        while self.running:
            time.sleep(1)
            with socket_lock:
                try:
                    self.socket.settimeout(0.5)
                    message = self.get_messages()
                except OSError as e:
                    if e.errno:
                        logger.critical(f"Lost connection to server!")
                        self.running = False
                        self.connection_lost.emit()
                except (
                    ConnectionError,
                    ConnectionAbortedError,
                    ConnectionResetError,
                    TypeError,
                ):
                    logger.critical(f"Connection timed out!")
                    self.running = False
                    self.connection_lost.emit()
                else:
                    logger.debug(f"Got message: {message}")
                finally:
                    self.socket.settimeout(5)

    def _create_socket(self) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.connect((self.addr, self.port))
        logger.info(f"Connected to {self.addr}:{self.port}")

    def _init_client(self) -> None:
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

    def _make_add_contact_message(self, contact: str) -> AddContactRequest:
        return AddContactRequest(
            action="add_contact",
            time=datetime.now().timestamp(),
            user_login=self.account_name,
            contact=contact,
        )

    def _make_del_contact_message(self, contact: str) -> DelContactRequest:
        return DelContactRequest(
            action="del_contact",
            time=datetime.now().timestamp(),
            user_login=self.account_name,
            contact=contact,
        )

    def _make_get_all_users_message(self) -> GetUsersRequest:
        return GetUsersRequest(
            action="get_users",
            time=datetime.now().timestamp(),
            user_login=self.account_name,
        )

    def _send_presence_message(self, status: str) -> None:
        presence_message = self._make_presence_message(status=status)
        with socket_lock:
            send_message(conn=self.socket, message=presence_message)
            logger.info("Presence message sent")
            msg = recv_message(conn=self.socket)
            logger.info(f"Response: {msg}")

    def _get_contacts(self) -> None:
        get_contacts_message = self._make_get_contacts_message()
        with socket_lock:
            send_message(conn=self.socket, message=get_contacts_message)
            logger.info("Contacts message sent")
            while True:
                msg = recv_message(conn=self.socket)
                if msg.get("response") == 202:
                    logger.info(f"Got contact list: {msg.get('alert')}")
                    break
        self.storage.update_contact_list(contact_list=msg.get("alert"))

    def get_all_users(self) -> list[str]:
        get_all_users_message = self._make_get_all_users_message()
        with socket_lock:
            send_message(conn=self.socket, message=get_all_users_message)
            logger.info("Get all users message sent")
            while True:
                msg = recv_message(conn=self.socket)
                if msg.get("response") == 202:
                    logger.info(f"Got user list: {msg.get('alert')}")
                    return msg.get("alert")

    def add_contact(self, contact: str) -> None:
        add_contact_message = self._make_add_contact_message(contact=contact)
        with socket_lock:
            send_message(conn=self.socket, message=add_contact_message)
            logger.info("Add contact message sent")
            while True:
                msg = recv_message(conn=self.socket)
                if msg.get("response") == 200:
                    break
        self._get_contacts()

    def del_contact(self, contact: str) -> None:
        del_contact_message = self._make_del_contact_message(contact=contact)
        send_message(conn=self.socket, message=del_contact_message)
        logger.info("Del contact message sent")
        while True:
            msg = recv_message(conn=self.socket)
            if msg.get("response") == 200:
                break
        self._get_contacts()

    def make_text_message(self, to_chat: str, message: str) -> ChatMessageRequest:
        data = {
            "time": datetime.now().timestamp(),
            "to": to_chat,
            "from": self.account_name,
            "message": message,
        }
        return ChatMessageRequest(**data)

    def get_messages(self):
        with socket_lock:
            try:
                msg = recv_message(conn=self.socket)
                logger.info(f"Message received: {msg}")
            except ReceiveError:
                logger.warning("Invalid message received (%s)", msg)
                raise
            except (
                OSError,
                ConnectionError,
                ConnectionAbortedError,
                ConnectionResetError,
            ):
                logger.critical("Connection lost!")
                self.stop()
                raise
            else:
                if msg.get("action") == "msg":
                    self.storage.save_message(
                        message_type=MessageType.income,
                        contact=msg.get("from"),
                        message=msg.get("message"),
                    )
                    self.new_message.emit(msg.get("from"))
                    return f"{msg.get('from')}: {msg.get('message')}"
                elif msg.get("action") == "presence":
                    return f"{msg.get('user', {}).get('account_name')} connected"

    def send_message(self, message: str, receiver: str):
        with socket_lock:
            try:
                send_message(
                    conn=self.socket,
                    message=self.make_text_message(
                        to_chat=receiver,
                        message=message,
                    ),
                )
            except (
                OSError,
                ConnectionError,
                ConnectionAbortedError,
                ConnectionResetError,
            ) as e:
                logger.critical("Connection lost!")
                raise e
                self.stop()
            else:
                self.storage.save_message(
                    message_type=MessageType.outcome, contact=receiver, message=message
                )


def main(addr: str, port: int = typer.Argument(default=7777)):
    client_app = QApplication(sys.argv)

    start_dialog = UserNameDialog()
    client_app.exec()
    if start_dialog.ok_pressed:
        account_name = start_dialog.client_name.text()
        del start_dialog
    else:
        exit(0)

    db_file_postfix = re.compile(r"[^a-zA-Z0-9_]+").sub("", account_name).lower()
    storage = ClientDatabase(db_file_postfix=db_file_postfix)
    client = JimClient(
        addr=addr,
        port=port,
        account_name=account_name,
        storage=storage,
    )
    client.daemon = True
    client.start()

    main_window = ClientMainWindow(database=storage, client=client)
    main_window.make_connection(client)
    main_window.setWindowTitle(f"Async GB messanger - {account_name}")
    client_app.exec()

    client.stop()


if __name__ == "__main__":
    typer.run(main)
