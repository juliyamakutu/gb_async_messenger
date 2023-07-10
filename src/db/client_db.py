from datetime import datetime

from sqlalchemy import (Column, DateTime, Integer, MetaData, String, Table,
                        create_engine)
from sqlalchemy.orm import registry, sessionmaker

from config import client_config as config


class ClientDatabase:
    class MessageHistory:
        def __init__(self, contact: str, message: str):
            self.contact = contact
            self.message = message
            self.time = datetime.now()

    class ContactList:
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

    def save_message(self, *, contact: str, message: str) -> None:
        message = self.MessageHistory(contact, message)
        self.session.add(message)
        self.session.commit()

    def update_contact_list(self, *, contact_list: list[str]) -> None:
        self.session.query(self.ContactList).delete()
        for contact in contact_list:
            contact = self.ContactList(contact)
            self.session.add(contact)
        self.session.commit()
