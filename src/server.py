import configparser
import os
import select
import sys
import threading
from collections import defaultdict
from queue import Queue
from socket import AF_INET, SOCK_STREAM, socket
from typing import Generator

from pydantic import ValidationError
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QMessageBox

from common import (AddContactRequest, ChatMessageRequest, DelContactRequest,
                    GetContactsRequest, GetUsersRequest, Port, PresenceRequest,
                    ReceiveError, Request, Response, ServerMeta, log,
                    recv_message, send_message)
from config import server_config as config
from db import ServerStorage
from log import server_logger as logger
from server_gui import (ClientsWindow, ConfigWindow, MainWindow,
                        create_active_clients_table, create_clients_table)


class JimServer(threading.Thread, metaclass=ServerMeta):
    port = Port()

    def __init__(self, addr: str, port: int, storage: "ServerStorage"):
        self.addr = addr
        self.port = port

        self.clients = []
        self.sent_count = defaultdict(int)
        self.recv_count = defaultdict(int)
        self.names = {}
        self.queues = {}

        self.storage = storage

        self.server = None
        self.running = True
        self._create_server()

        super().__init__()

    def run(self):
        while self.running:
            self.process_new_connections()
            self.check_socket()

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
        elif msg_action == "get_users":
            try:
                parsed_message = GetUsersRequest(**msg)
            except ValidationError:
                logger.warning("Invalid message: %s", msg)
                return None
            logger.info("Get users message received from user %s", msg["user_login"])
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
                elif parsed_message.action == "get_users":
                    user_login = parsed_message.user_login
                    self.names[user_login] = sender
                    self.queues[sender].put(
                        Response(
                            response=202,
                            alert=[
                                user[0]
                                for user in self.storage.get_all_clients(
                                    login=user_login
                                )
                            ],
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
                self.recv_count[connection] += 1
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
                else:
                    self.sent_count[connection] += 1

    def get_clients_statistics(self) -> Generator:
        for connection in self.clients:
            ip, port = connection.getpeername()
            login = ""
            for key, values in self.names.items():
                if values == connection:
                    login = key
            yield login, ip, port, self.sent_count[connection], self.recv_count[
                connection
            ]


if __name__ == "__main__":
    config_ini = configparser.ConfigParser()

    config_ini.read("server.ini")

    database = ServerStorage(
        os.path.join(
            config_ini["SETTINGS"]["Database_path"],
            config_ini["SETTINGS"]["Database_file"],
        )
    )

    server = JimServer(
        addr=config_ini["SETTINGS"]["Listen_Address"],
        port=int(config_ini["SETTINGS"]["Default_port"]),
        storage=database,
    )
    server.daemon = True
    server.start()

    server_app = QApplication(sys.argv)
    main_window = MainWindow()

    main_window.statusBar().showMessage("Server Working")
    main_window.active_clients_table.setModel(
        create_active_clients_table(server.get_clients_statistics())
    )
    main_window.active_clients_table.resizeColumnsToContents()
    main_window.active_clients_table.resizeRowsToContents()

    def list_update():
        main_window.active_clients_table.setModel(
            create_active_clients_table(server.get_clients_statistics())
        )
        main_window.active_clients_table.resizeColumnsToContents()
        main_window.active_clients_table.resizeRowsToContents()

    def show_all_clients():
        global all_clients_window
        all_clients_window = ClientsWindow()
        all_clients_window.clients_table.setModel(
            create_clients_table(database.get_all_clients())
        )
        all_clients_window.clients_table.resizeColumnsToContents()
        all_clients_window.clients_table.resizeRowsToContents()
        all_clients_window.show()

    def server_config():
        global config_window
        config_window = ConfigWindow()
        config_window.db_path.insert(config_ini["SETTINGS"]["Database_path"])
        config_window.db_file.insert(config_ini["SETTINGS"]["Database_file"])
        config_window.port.insert(config_ini["SETTINGS"]["Default_port"])
        config_window.ip.insert(config_ini["SETTINGS"]["Listen_Address"])
        config_window.save_btn.clicked.connect(save_server_config)

    def save_server_config():
        global config_window
        message = QMessageBox()

        port = config_window.port.text()
        if not port.isdecimal():
            message.warning(config_window, "Error", "Port must be integer")
            return
        if (int(port) < 1023) or (int(port) > 65536):
            message.warning(config_window, "Error", "Port must be from 1024 to 65536")
            return

        config_ini["SETTINGS"]["Database_path"] = config_window.db_path.text()
        config_ini["SETTINGS"]["Database_file"] = config_window.db_file.text()
        config_ini["SETTINGS"]["Listen_Address"] = config_window.ip.text()
        config_ini["SETTINGS"]["Default_port"] = port
        with open("server.ini", "w") as conf:
            config_ini.write(conf)
            message.information(config_window, "Ok", "Config saved")

    timer = QTimer()
    timer.timeout.connect(list_update)
    timer.start(1000)

    main_window.refresh_button.triggered.connect(list_update)
    main_window.show_all_clients_button.triggered.connect(show_all_clients)
    main_window.config_btn.triggered.connect(server_config)

    server_app.exec()
