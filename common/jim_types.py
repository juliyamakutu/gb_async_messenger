from pydantic import BaseModel


class Request(BaseModel):
    action: str
    time: str


class Response(BaseModel):
    response: int
    alert: str


class PresenceRequest(Request):
    class User(BaseModel):
        account_name: str
        status: str

    action: str = "presence"
    type: str | None
    user: User
