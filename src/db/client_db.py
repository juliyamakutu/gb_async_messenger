from datetime import datetime
from enum import Enum

from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table,
                        create_engine)
from sqlalchemy.orm import registry, sessionmaker


class MessageType(Enum):
    income = "income"
    outcome = "outcome"


class ClientDatabase:
    """Класс - база данных клиента."""

    class MessageHistory:
        """Класс - отображение таблицы истории сообщений."""

        def __init__(self, message_type: MessageType, contact: str, message: str):
            self.message_type = message_type
            self.contact = contact
            self.message = message
            self.time = datetime.now()

    class ContactList:
        """Класс - отображение списка контактов."""

        def __init__(self, contact: str):
            self.contact = contact

    def __init__(self, db_file_postfix: str):
        self.database_engine = create_engine(
            f"sqlite:///client_{db_file_postfix}.db", echo=False, pool_recycle=7200
        )
        self.metadata = MetaData()

        message_history = Table(
            "message_history",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("message_type", String),
            Column("contact", String),
            Column("message", String),
            Column("time", DateTime),
        )
        contact_list = Table(
            "contact_list",
            self.metadata,
            Column("id", Integer, primary_key=True),
            Column("contact", String),
        )

        self.metadata.create_all(self.database_engine)

        mapper_registry = registry()
        mapper_registry.map_imperatively(self.MessageHistory, message_history)
        mapper_registry.map_imperatively(self.ContactList, contact_list)

        self.session = sessionmaker(bind=self.database_engine)()

    def save_message(
        self, *, message_type: MessageType, contact: str, message: str
    ) -> None:
        """Сохраняет сообщение в базу данных."""
        message = self.MessageHistory(message_type, contact, message)
        self.session.add(message)
        self.session.commit()

    def update_contact_list(self, *, contact_list: list[str]) -> None:
        """Обновляет список контактов."""
        self.session.query(self.ContactList).delete()
        for contact in contact_list:
            contact = self.ContactList(contact)
            self.session.add(contact)
        self.session.commit()

    def get_contacts(self) -> list[str]:
        """Возвращает список контактов."""
        return [
            contact.contact for contact in self.session.query(self.ContactList).all()
        ]

    def get_history(self, contact: str) -> list[tuple[str, str, str, datetime]]:
        """Возвращает историю переписки с указанным контактом."""
        return [
            (
                message_history.message_type,
                message_history.contact,
                message_history.message,
                message_history.time,
            )
            for message_history in self.session.query(self.MessageHistory)
            .filter_by(contact=contact)
            .all()
        ]

    def check_contact(self, contact: str) -> bool:
        """Проверяет наличие контакта в списке контактов."""
        return bool(
            self.session.query(self.ContactList).filter_by(contact=contact).count()
        )
