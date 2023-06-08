from pydantic import BaseSettings


class CommonSettings(BaseSettings):
    bytes_to_recv: int = 1024
    encoding = "utf-8"


class ServerSettings(CommonSettings):
    host: str = ""
    port: int = 7777
    max_connections: int = 5


class ClientSettings(CommonSettings):
    host: str = "localhost"
    port: int = 7777


base_config = CommonSettings()
client_config = ClientSettings()
server_config = ServerSettings()