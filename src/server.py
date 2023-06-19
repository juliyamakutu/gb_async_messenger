import select
import sys
from socket import AF_INET, SOCK_STREAM, socket

import typer
from pydantic import ValidationError
from typing_extensions import Annotated

from common import (PresenceRequest, ReceiveError, Response, Request, ChatMessageRequest, recv_message,
                    send_message, log)
from config import server_config as config
from log import server_logger as logger


@log(logger)
def parse_message(msg: dict) -> Request | None:
    msg_action = msg.get("action")
    if msg_action == "presence":
        try:
            PresenceRequest(**msg)
        except ValidationError:
            logger.warning("Invalid presence message: %s", msg)
            return None
        logger.info("Presence message received from user %s", msg["user"]["account_name"])
    if msg_action == "msg":
        try:
            ChatMessageRequest(**msg)
        except ValidationError:
            logger.warning("Invalid message: %s", msg)
            return None
        logger.info("Message received from user %s", msg["from"])
    else:
        logger.warning("Unknown message type: %s", msg_action)
        return None


@log(logger)
def parse_messages(messages: dict) -> (dict, dict):
    parsed_messages = {}
    responses = {}
    for sender, message in messages.items():
        parsed_message = parse_message(message)
        if not parsed_message:
            responses[sender] = Response(response=400, alert="Invalid message")
        else:
            responses[sender] = Response(response=200, alert="OK")
            parsed_messages[sender] = parse_message(message)
    return parsed_messages, responses


@log(logger)
def read_clients(clients: list, all_clients: list) -> dict:
    messages = {}
    for client in clients:
        try:
            msg = recv_message(conn=client)
        except ReceiveError:
            logger.warning("Invalid message received from client %s", client.getpeername())
            continue
        except:
            logger.error("Client %s disconnected", client.getpeername())
            all_clients.remove(client)
            continue
        messages[client] = msg
    return messages


@log(logger)
def write_clients(clients: list, all_clients: list, messages: dict) -> None:
    for client in clients:
        for sender, message in messages:
            if sender != client:
                try:
                    send_message(conn=client, message=message)
                except:
                    logger.error("Client %s disconnected", client.getpeername())
                    all_clients.remove(client)
                    continue


@log(logger)
def write_response(responses: dict, all_clients: list) -> None:
    for client, message in responses.items():
        try:
            send_message(conn=client, message=message)
        except:
            logger.error("Client %s disconnected", client.getpeername())
            all_clients.remove(client)
            continue


def main(
    host: Annotated[str, typer.Option("-a")] = config.host,
    port: Annotated[int, typer.Option("-p")] = config.port,
):
    clients = []
    s = socket(AF_INET, SOCK_STREAM)
    s.bind((host, port))
    s.listen(config.max_connections)
    s.settimeout(config.socket_timeout)
    logger.info("Server started on %s:%s", host, port)
    try:
        while True:
            try:
                conn, addr = s.accept()
            except OSError:
                pass
            else:
                logger.info(f"Connected by %s", addr)
                clients.append(conn)
            finally:
                read_list = []
                write_list = []
                try:
                    read_list, write_list, _ = select.select(clients, clients, [], 10)
                except:
                    pass
                message = read_clients(clients=read_list, all_clients=clients)
                parsed_messages, responses = parse_messages(messages=message)
                write_response(responses=responses, all_clients=clients)
                write_clients(clients=write_list, all_clients=clients, messages=responses)

    except KeyboardInterrupt:
        logger.info("Server stopped by user")
        s.close()
        sys.exit()
    finally:
        logger.info("Server stopped")
        s.close()


if __name__ == "__main__":
    typer.run(main)
