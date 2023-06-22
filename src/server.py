import select
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from common import (PresenceRequest, ReceiveError, Response, Request, ChatMessageRequest, recv_message,
                    send_message, log)
from config import server_config as config
from log import server_logger as logger
from queue import Queue


@log(logger)
def parse_message(msg: dict) -> Request | None:
    msg_action = msg.get("action")
    if msg_action == "presence":
        try:
            parsed_message = PresenceRequest(**msg)
        except ValidationError:
            logger.warning("Invalid presence message: %s", msg)
            return None
        logger.info("Presence message received from user %s", msg["user"]["account_name"])
    elif msg_action == "msg":
        try:
            parsed_message = ChatMessageRequest(**msg)
        except ValidationError:
            logger.warning("Invalid message: %s", msg)
            return None
        logger.info("Message received from user %s", msg["from"])
    else:
        logger.warning("Unknown message type: %s", msg_action)
        return None
    return parsed_message


@log(logger)
def process_messages(messages: dict, names: dict, queues: dict) -> None:
    for sender, message in messages.items():
        parsed_message = parse_message(message)
        if not parsed_message:
            queues[sender].put(Response(response=400, alert="Invalid message"))
        else:
            queues[sender].put(Response(response=200, alert="OK"))
            if parsed_message.action == "presence":
                names[parsed_message.user.account_name] = sender
            elif parsed_message.action == "msg":
                names[parsed_message.from_account] = sender
                receiver = names.get(parsed_message.to_chat)
                if receiver:
                    queues[receiver].put(parsed_message)


def read_clients(clients: list, all_clients: list) -> dict:
    messages = {}
    for client in clients:
        try:
            msg = recv_message(conn=client)
        except ReceiveError:
            logger.warning("Invalid message received from client")
            continue
        except (OSError, ConnectionResetError):
            logger.error("Client disconnected")
            all_clients.remove(client)
            continue
        if msg:
            messages[client] = msg
    return messages


def send_messages(clients: list, all_clients: list, queues: dict, names: dict) -> None:
    for client in clients:
        if not queues[client].empty():
            message = queues[client].get()
            try:
                send_message(conn=client, message=message)
            except (OSError, ConnectionResetError):
                logger.error("Client disconnected")
                all_clients.remove(client)
                del queues[client]
                for key, values in names.items():
                    if values == client:
                        del names[key]
                continue

def main(
    host: Annotated[str, typer.Option("-a")] = config.host,
    port: Annotated[int, typer.Option("-p")] = config.port,
):
    clients = []
    names = {}
    queues = {}

    with socket(AF_INET, SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(config.max_connections)
        s.settimeout(config.socket_timeout)
        logger.info("Server started on %s:%s", host, port)
        while True:
            try:
                conn, addr = s.accept()
            except OSError:
                pass
            else:
                logger.info(f"Connected by %s", addr)
                clients.append(conn)
                queues[conn] = Queue()
            finally:
                read_list = []
                write_list = []
                messages = {}
                if clients:
                    try:
                        read_list, write_list, _ = select.select(clients, clients, [], 10)
                    except OSError:
                        pass
                if read_list:
                    messages = read_clients(clients=read_list, all_clients=clients)
                if messages:
                    process_messages(messages=messages, names=names, queues=queues)
                if write_list:
                    send_messages(clients=write_list, all_clients=clients, queues=queues, names=names)


if __name__ == "__main__":
    typer.run(main)
