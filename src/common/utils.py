import json
import sys
from ipaddress import ip_address
from socket import socket
from subprocess import PIPE, Popen

from tabulate import tabulate

from config import base_config as config
from log import client_logger, server_logger

from .exceptions import ReceiveError
from .jim_types import Request, Response

if "server" in sys.argv[0]:
    logger = server_logger
else:
    logger = client_logger


# @log(logger)
def send_message(conn: socket, message: Request | Response) -> None:
    """Отправка сообщения в формате JIM в сокет"""
    conn.send(message.json(by_alias=True).encode(encoding=config.encoding))


# @log(logger)
def recv_message(conn: socket) -> dict | None:
    """Получение сообщения из сокета"""
    msg_bytes = conn.recv(config.bytes_to_recv)
    if len(msg_bytes) == 0:
        return None
    try:
        return json.loads(msg_bytes.decode(encoding=config.encoding))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ReceiveError


def _host_ping(host: str, timeout: int = 1):
    try:
        ip = ip_address(host)
    except ValueError:
        # if it is host name
        ip = host
    ping = Popen(["ping", "-c", "1", "-t", "1", str(ip)], shell=False, stdout=PIPE)
    ping.wait()
    if ping.returncode == 0:
        return True
    else:
        return False


def host_ping(host_list: list[str]):
    for host in host_list:
        if _host_ping(host):
            print(f"Узел {host} доступен")
        else:
            print(f"Узел {host} недоступен")


def host_range_ping(start_ip: str, ip_count: int):
    first_bytes = ".".join(start_ip.split(".")[:-1])
    last_byte = start_ip.split(".")[-1]
    max_ip = int(last_byte) + ip_count
    if max_ip > 254:
        max_ip = 254
    for i in range(int(last_byte), max_ip):
        host = f"{first_bytes}.{i}"
        if _host_ping(host):
            print(f"Узел {host} доступен")
        else:
            print(f"Узел {host} недоступен")


def host_range_ping_tab(start_ip: str, ip_count: int):
    first_bytes = ".".join(start_ip.split(".")[:-1])
    last_byte = start_ip.split(".")[-1]
    max_ip = int(last_byte) + ip_count
    if max_ip > 254:
        max_ip = 254
    result = {"Available hosts": [], "Unavailable hosts": []}
    for i in range(int(last_byte), max_ip):
        host = f"{first_bytes}.{i}"
        if _host_ping(host):
            result["Available hosts"].append(str(host))
        else:
            result["Unavailable hosts"].append(str(host))
    print(tabulate(result, headers="keys", tablefmt="pipe", stralign="center"))
