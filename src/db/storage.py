from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config import server_config as config

engine = create_engine(
    config.database_path, echo=config.database_log, pool_recycle=config.database_recycle
)
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


class ServerStorage:
    def __init__(self):
        self.session = sessionmaker(bind=engine)()

    def _client_history(self, client_id: int, ip_address: str, port: int) -> None:
        client_history = ClientHistory(
            client_id=client_id,
            last_login=datetime.now(),
            ip_address=ip_address,
            port=port,
        )
        self.session.add(client_history)
        self.session.commit()

    def client_loging(self, *, login: str, ip_address: str, port: int) -> None:
        client = self.session.query(Client).filter_by(login=login).first()
        if not client:
            client = Client(login=login)
            self.session.add(client)
            self.session.commit()
        self._client_history(client.id, ip_address, port)

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
