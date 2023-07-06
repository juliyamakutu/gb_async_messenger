import select
from queue import Queue
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from common import (AddContactRequest, ChatMessageRequest, DelContactRequest,
                    GetContactsRequest, Port, PresenceRequest, ReceiveError,
                    Request, Response, ServerMeta, log, recv_message,
                    send_message)
from config import server_config as config
from db import ServerStorage
from log import server_logger as logger


class JimServer(metaclass=ServerMeta):
    port = Port()

    def __init__(self, addr: str, port: int, storage: "ServerStorage"):
        self.addr = addr
        self.port = port

        self.clients = []
        self.names = {}
        self.queues = {}

        self.storage = storage

        self.server = None
        self.running = True
        self._create_server()

    def _create_server(self) -> None:
        self.server = socket(AF_INET, SOCK_STREAM)
        self.server.bind((self.addr, self.port))
        self.server.listen(config.max_connections)
        self.server.settimeout(config.socket_timeout)
        logger.info("Server started on %s:%s", self.addr, self.port)

    def stop(self):
        for client in self.clients:
            client.close()
        self.running = False
        self.server.close()

    def process_new_connections(self):
        try:
            client, client_address = self.server.accept()
        except OSError:
            pass
        else:
            logger.info("Client %s connected", client_address)
            self.clients.append(client)
            self.queues[client] = Queue()

    def check_socket(self):
        read_list = []
        write_list = []
        messages = {}
        if self.clients:
            try:
                read_list, write_list, _ = select.select(
                    self.clients, self.clients, [], 10
                )
            except OSError:
                pass
        if read_list:
            messages = self.read_clients(read_list=read_list)
        if messages:
            self.process_messages(messages=messages)
        if write_list:
            self.send_messages(write_list=write_list)

    @staticmethod
    def parse_message(msg: dict) -> Request | None:
        msg_action = msg.get("action")
        if msg_action == "presence":
            try:
                parsed_message = PresenceRequest(**msg)
            except ValidationError:
                logger.warning("Invalid presence message: %s", msg)
                return None
            logger.info(
                "Presence message received from user %s", msg["user"]["account_name"]
            )
        elif msg_action == "msg":
            try:
                parsed_message = ChatMessageRequest(**msg)
            except ValidationError:
                logger.warning("Invalid message: %s", msg)
                return None
            logger.info("Message received from user %s", msg["from"])
        elif msg_action == "get_contacts":
            try:
                parsed_message = GetContactsRequest(**msg)
            except ValidationError:
                logger.warning("Invalid message: %s", msg)
                return None
            logger.info("Get contacts message received from user %s", msg["user_login"])
        elif msg_action == "add_contact":
            try:
                parsed_message = AddContactRequest(**msg)
            except ValidationError:
                logger.warning("Invalid message: %s", msg)
                return None
            logger.info("Add contact message received from user %s", msg["user_login"])
        elif msg_action == "del_contact":
            try:
                parsed_message = DelContactRequest(**msg)
            except ValidationError:
                logger.warning("Invalid message: %s", msg)
                return None
            logger.info("Del contact message received from user %s", msg["user_login"])
        else:
            logger.warning("Unknown message type: %s", msg_action)
            return None
        return parsed_message

    @log(logger)
    def process_messages(self, messages: dict) -> None:
        for sender, message in messages.items():
            parsed_message = self.parse_message(message)
            if not parsed_message:
                self.queues[sender].put(Response(response=400, alert="Invalid message"))
            else:
                if parsed_message.action == "presence":
                    account_name = parsed_message.user.account_name
                    ip_address, port = sender.getpeername()
                    self.names[account_name] = sender
                    self.storage.client_loging(
                        login=account_name, ip_address=ip_address, port=port
                    )
                    self.queues[sender].put(Response(response=200, alert="OK"))
                elif parsed_message.action == "msg":
                    from_account = parsed_message.from_account
                    self.names[from_account] = sender
                    to_chat = parsed_message.to_chat
                    if receiver := self.names.get(to_chat):
                        self.queues[receiver].put(parsed_message)
                        self.storage.add_contact(
                            login=to_chat, contact_login=from_account
                        )
                    self.queues[sender].put(Response(response=200, alert="OK"))
                elif parsed_message.action == "get_contacts":
                    user_login = parsed_message.user_login
                    self.names[user_login] = sender
                    self.queues[sender].put(
                        Response(
                            response=202,
                            alert=self.storage.get_contact_list(login=user_login),
                        )
                    )
                elif parsed_message.action == "add_contact":
                    user_login = parsed_message.user_login
                    contact_login = parsed_message.contact_login
                    self.names[user_login] = sender
                    self.storage.add_contact(
                        login=user_login, contact_login=contact_login
                    )
                    self.queues[sender].put(
                        Response(
                            response=200,
                        )
                    )
                elif parsed_message.action == "del_contact":
                    user_login = parsed_message.user_login
                    contact_login = parsed_message.contact_login
                    self.names[user_login] = sender
                    self.storage.del_contact(
                        login=user_login, contact_login=contact_login
                    )
                    self.queues[sender].put(
                        Response(
                            response=200,
                        )
                    )

    def read_clients(self, read_list: list) -> dict:
        messages = {}
        for connection in read_list:
            try:
                msg = recv_message(conn=connection)
            except ReceiveError:
                logger.warning("Invalid message received from client")
                continue
            except (OSError, ConnectionResetError):
                logger.error("Client disconnected")
                self.clients.remove(connection)
                continue
            if msg:
                messages[connection] = msg
        return messages

    def send_messages(self, write_list: list) -> None:
        for connection in write_list:
            if not self.queues[connection].empty():
                message = self.queues[connection].get()
                try:
                    send_message(conn=connection, message=message)
                except (OSError, ConnectionResetError):
                    logger.warning("Client disconnected")
                    self.clients.remove(connection)
                    del self.queues[connection]
                    for key, values in self.names.items():
                        if values == connection:
                            del self.names[key]
                    continue


def main(
    host: Annotated[str, typer.Option("-a")] = config.host,
    port: Annotated[int, typer.Option("-p")] = config.port,
):
    server = JimServer(addr=host, port=port, storage=ServerStorage())
    while server.running:
        try:
            server.process_new_connections()
            server.check_socket()
        except Exception as e:
            logger.critical(e)
            server.stop()
            raise
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            server.stop()
            break
    server.stop()


if __name__ == "__main__":
    typer.run(main)
