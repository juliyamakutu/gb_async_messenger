from datetime import datetime
from typing import Generator

import bcrypt
from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import server_config as config

Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)


class ClientHistory(Base):
    __tablename__ = "client_history"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    last_login = Column(DateTime)
    ip_address = Column(String)
    port = Column(Integer)


class ContactList(Base):
    __tablename__ = "contact_list"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer)
    contact_id = Column(Integer)


class Users(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    login = Column(String, unique=True)
    password = Column(String)
    salt = Column(String)


class ServerStorage:
    def __init__(self, database_path: str):
        self._engine = create_engine(
            f"sqlite:///{database_path}",
            echo=config.database_log,
            pool_recycle=config.database_recycle,
        )
        self.session = sessionmaker(bind=self._engine)()

    def _client_history(self, client_id: int, ip_address: str, port: int) -> None:
        client_history = ClientHistory(
            client_id=client_id,
            last_login=datetime.now(),
            ip_address=ip_address,
            port=port,
        )
        self.session.add(client_history)
        self.session.commit()

    def user_exists(self, login: str) -> bool:
        return self.session.query(Users).filter_by(login=login).count() > 0

    def check_user_password(self, login: str, password: str) -> bool:
        user = self.session.query(Users).filter_by(login=login).first()
        if user:
            password_hash = bcrypt.hashpw(password.encode(), user.salt)
            if user.password == password_hash:
                return True
        return False

    def add_user(self, login: str, password: str) -> None:
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode(), salt)
        user = Users(login=login, password=password_hash, salt=salt)
        self.session.add(user)
        self.session.commit()

    def client_loging(self, *, login: str, ip_address: str, port: int) -> None:
        client = self.session.query(Client).filter_by(login=login).first()
        if not client:
            client = Client(login=login)
            self.session.add(client)
            self.session.commit()
        self._client_history(client.id, ip_address, port)

    def get_all_clients(self) -> Generator:
        clients = self.session.query(Client).all()
        for client in clients:
            client_history = (
                self.session.query(ClientHistory)
                .filter_by(client_id=client.id)
                .order_by(ClientHistory.last_login.desc())
                .first()
            )
            yield client.login, client_history.last_login, client_history.ip_address, client_history.port

    def add_contact(self, *, login: str, contact_login: str) -> None:
        client = self.session.query(Client).filter_by(login=login).first()
        contact = self.session.query(Client).filter_by(login=contact_login).first()
        if not client or not contact:
            return
        if (
            not self.session.query(ContactList)
            .filter_by(client_id=client.id, contact_id=contact.id)
            .first()
        ):
            contact_record = ContactList(client_id=client.id, contact_id=contact.id)
            self.session.add(contact_record)
            self.session.commit()

    def del_contact(self, *, login: str, contact_login: str) -> None:
        client = self.session.query(Client).filter_by(login=login).first()
        contact = self.session.query(Client).filter_by(login=contact_login).first()
        if not client or not contact:
            return
        contact_record = (
            self.session.query(ContactList)
            .filter_by(client_id=client.id, contact_id=contact.id)
            .first()
        )
        if contact_record:
            self.session.delete(contact_record)
            self.session.commit()

    def get_contact_list(self, *, login: str) -> list:
        client = self.session.query(Client).filter_by(login=login).first()
        if not client:
            return []
        contacts = self.session.query(ContactList).filter_by(client_id=client.id).all()

        contact_list = map(
            lambda contact: self.session.query(Client)
            .filter_by(id=contact.contact_id)
            .first(),
            contacts,
        )
        return [contact.login for contact in contact_list]
