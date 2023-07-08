import logging

from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    bytes_to_recv: int = 1024
    encoding = "utf-8"
    log_format = "%(asctime)s %(levelname)s %(filename)s %(message)s"
    log_level: int = logging.INFO


class ServerSettings(CommonSettings):
    host: str = ""
    port: int = 7777
    max_connections: int = 5
    socket_timeout: float = 0.2
    log_interval: int = 1
    log_period: str = "D"
    database_log: bool = False
    database_recycle: int = 7200


class ClientSettings(CommonSettings):
    host: str = "localhost"
    port: int = 7777
    database_path: str = "sqlite:///client.db"


base_config = CommonSettings()
client_config = ClientSettings()
server_config = ServerSettings()
