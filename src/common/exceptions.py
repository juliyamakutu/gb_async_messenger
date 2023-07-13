class ReceiveError(Exception):
    """Raised when a recive error occurs."""

    pass


class PortValueError(Exception):
    """Raised when a port error occurs."""

    pass


class ServerError(Exception):
    """Raised when a server error occurs."""

    pass


class AccessDeniedError(Exception):
    """Raised when a user not authenticated."""

    pass
