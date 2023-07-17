from pydantic import BaseModel, Field


class Request(BaseModel):
    """Базовый класс для запросов"""

    action: str
    time: str


class Response(BaseModel):
    """Базовый класс для ответов"""

    response: int
    alert: str | list | None = None


class PresenceRequest(Request):
    """Класс уведомления о присутствии"""

    class User(BaseModel):
        account_name: str
        status: str

    action: str = "presence"
    type: str | None
    user: User


class AuthRequest(Request):
    """Класс запроса аутентификации"""

    class User(BaseModel):
        account_name: str
        password: str

    action = "authenticate"
    user: User


class ChatMessageRequest(Request):
    """Класс отправки сообщения"""

    action = "msg"
    to_chat: str = Field(alias="to")
    from_account: str = Field(alias="from")
    message: str


class GetContactsRequest(Request):
    """Класс запроса списка контактов"""

    action = "get_contacts"
    user_login: str


class AddContactRequest(Request):
    """Класс запроса добавления контакта"""

    action = "add_contact"
    user_id: str
    user_login: str


class DelContactRequest(Request):
    """Класс запроса удаления контакта"""

    action = "del_contact"
    user_id: str
    user_login: str


class GetUsersRequest(Request):
    """Класс запроса списка пользователей"""

    action = "get_users"
    user_login: str
