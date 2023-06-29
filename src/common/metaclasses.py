import dis
import sys

from log import client_logger, server_logger

from .exceptions import PortValueError

if "server" in sys.argv[0]:
    logger = server_logger
else:
    logger = client_logger


class Port:
    def __set__(self, obj, value):
        if (value < 1024) or (value > 65536):
            logger.critical(f"Wrong port number {value}")
            raise PortValueError(
                f"Allowed port numbers are from 1024 to 65535, but received {value}"
            )
        setattr(obj, self.private_name, value)

    def __get__(self, obj, obj_type):
        return getattr(obj, self.private_name, None)

    def __set_name__(self, owner, name):
        self.public_name = name
        self.private_name = "_" + name


class ServerMeta(type):
    def __init__(self, clsname, bases, clsdict):
        instructions = []
        for attr, value in clsdict.items():
            if attr.startswith("__"):
                continue
            if callable(value):
                for element in dis.get_instructions(value):
                    instructions.append(element.argval)
        if "connect" in instructions:
            raise TypeError('Method "connect" forbidden in server class')
        if not ("SOCK_STREAM" in instructions and "AF_INET" in instructions):
            raise TypeError("Incorrect socket initialization")
        super().__init__(clsname, bases, clsdict)


class ClientMeta(type):
    def __init__(self, clsname, bases, clsdict):
        instructions = []
        for attr, value in clsdict.items():
            if attr.startswith("__"):
                continue
            if callable(value):
                for element in dis.get_instructions(value):
                    instructions.append(element.argval)
        if "accept" in instructions or "listen" in instructions:
            raise TypeError('Methods "accept" and "listen" forbidden in client class')
        if not ("SOCK_STREAM" in instructions and "AF_INET" in instructions):
            raise TypeError("Incorrect socket initialization")

        super().__init__(clsname, bases, clsdict)
