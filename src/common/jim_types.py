from pydantic import BaseModel, Field


class Request(BaseModel):
    action: str
    time: str


class Response(BaseModel):
    response: int
    alert: str | list | None = None


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


class GetContactsRequest(Request):
    action = "get_contacts"
    user_login: str


class AddContactRequest(Request):
    action = "add_contact"
    user_id: str
    user_login: str


class DelContactRequest(Request):
    action = "del_contact"
    user_id: str
    user_login: str


class GetUsersRequest(Request):
    action = "get_users"
    user_login: str
