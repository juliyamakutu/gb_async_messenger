from pydantic import BaseModel, Field


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


class ChatMessageRequest(Request):
    action = "msg"
    to_chat: str = Field(alias="to")
    from_account: str = Field(alias="from")
    message: str
