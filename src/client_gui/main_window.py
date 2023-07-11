import sys

from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QBrush, QColor, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox, qApp

from log import client_logger, server_logger

from ..db import MessageType
from .add_contact import AddContactDialog
from .client_design import Ui_MainClientWindow
from .del_contact import DelContactDialog

sys.path.append("../")

if "server" in sys.argv[0]:
    logger = server_logger
else:
    logger = client_logger


class ClientMainWindow(QMainWindow):
    def __init__(self, database, client):
        super().__init__()
        self.database = database
        self.client = client

        self.ui = Ui_MainClientWindow()
        self.ui.setupUi(self)

        self.ui.menu_exit.triggered.connect(QApplication.instance().quit)

        self.ui.btn_send.clicked.connect(self.send_message)

        self.ui.btn_add_contact.clicked.connect(self.add_contact_window)
        self.ui.menu_add_contact.triggered.connect(self.add_contact_window)

        self.ui.btn_remove_contact.clicked.connect(self.delete_contact_window)
        self.ui.menu_del_contact.triggered.connect(self.delete_contact_window)

        self.contacts_model = None
        self.history_model = None
        self.messages = QMessageBox()
        self.current_chat = None
        self.ui.list_messages.setHorizontalScrollBarPolicy(
            Qt.WidgetAttribute.ScrollBarAlwaysOff
        )
        self.ui.list_messages.setWordWrap(True)

        self.ui.list_contacts.doubleClicked.connect(self.select_active_user)

        self.clients_list_update()
        self.set_disabled_input()
        self.show()

    def set_disabled_input(self):
        self.ui.label_new_message.setText("Double click on contact to start messaging")
        self.ui.text_message.clear()
        if self.history_model:
            self.history_model.clear()

        self.ui.btn_clear.setDisabled(True)
        self.ui.btn_send.setDisabled(True)
        self.ui.text_message.setDisabled(True)

    def history_list_update(self):
        lst = sorted(
            self.database.get_history(self.current_chat), key=lambda item: item[3]
        )
        if not self.history_model:
            self.history_model = QStandardItemModel()
            self.ui.list_messages.setModel(self.history_model)
        self.history_model.clear()
        length = len(lst)
        start_index = 0
        if length > 20:
            start_index = length - 20
        for i in range(start_index, length):
            item = lst[i]
            if item[0] == "income":
                mess = QStandardItem(
                    f"Income from {item[1].replace(microsecond=0)}:\n {item[2]}"
                )
                mess.setEditable(False)
                mess.setBackground(QBrush(QColor(255, 213, 213)))
                mess.setTextAlignment(Qt.WidgetAttribute.AlignLeft)
                self.history_model.appendRow(mess)
            else:
                mess = QStandardItem(
                    f"Outcome to {item[1].replace(microsecond=0)}:\n {item[2]}"
                )
                mess.setEditable(False)
                mess.setTextAlignment(Qt.WidgetAttribute.AlignRight)
                mess.setBackground(QBrush(QColor(204, 255, 204)))
                self.history_model.appendRow(mess)
        self.ui.list_messages.scrollToBottom()

    def select_active_user(self):
        self.current_chat = self.ui.list_contacts.currentIndex().data()
        self.set_active_user()

    def set_active_user(self):
        self.ui.label_new_message.setText(f"Enter message for {self.current_chat}:")
        self.ui.btn_clear.setDisabled(False)
        self.ui.btn_send.setDisabled(False)
        self.ui.text_message.setDisabled(False)

        self.history_list_update()

    def clients_list_update(self):
        contacts_list = self.database.get_contacts()
        self.contacts_model = QStandardItemModel()
        for i in sorted(contacts_list):
            item = QStandardItem(i)
            item.setEditable(False)
            self.contacts_model.appendRow(item)
        self.ui.list_contacts.setModel(self.contacts_model)

    def add_contact_window(self):
        global select_dialog
        select_dialog = AddContactDialog(self.client, self.database)
        select_dialog.btn_ok.clicked.connect(
            lambda: self.add_contact_action(select_dialog)
        )
        select_dialog.show()

    def add_contact_action(self, item):
        new_contact = item.selector.currentText()
        self.add_contact(new_contact)
        item.close()

    def add_contact(self, new_contact):
        try:
            self.client.add_contact(new_contact)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, "Error", "Lost connection to server!")
                self.close()
            self.messages.critical(self, "Error", "Connection timeout!")
        else:
            new_contact = QStandardItem(new_contact)
            new_contact.setEditable(False)
            self.contacts_model.appendRow(new_contact)
            logger.info(f"Contact {new_contact} successfully added")
            self.messages.information(self, "Success", "Contact successfully added.")

    def delete_contact_window(self):
        global remove_dialog
        remove_dialog = DelContactDialog(self.database)
        remove_dialog.btn_ok.clicked.connect(lambda: self.delete_contact(remove_dialog))
        remove_dialog.show()

    def delete_contact(self, item):
        selected = item.selector.currentText()
        try:
            self.client.del_contact(selected)
        except OSError as err:
            if err.errno:
                self.messages.critical(self, "Error", "Lost connection to server!")
                self.close()
            self.messages.critical(self, "Error", "Connection timeout!")
        else:
            self.clients_list_update()
            logger.info(f"Contact {selected} successfully deleted")
            self.messages.information(self, "Success", "Contact successfully deleted.")
            item.close()
            if selected == self.current_chat:
                self.current_chat = None
                self.set_disabled_input()

    def send_message(self):
        message_text = self.ui.text_message.toPlainText()
        self.ui.text_message.clear()
        if not message_text:
            return
        try:
            self.client.send_message(message=message_text, receiver=self.current_chat)
            pass
        except OSError as err:
            if err.errno:
                self.messages.critical(self, "Error", "Lost connection to server!")
                self.close()
            self.messages.critical(self, "Error", "Connection timeout!")
        except (ConnectionResetError, ConnectionAbortedError):
            self.messages.critical(self, "Error", "Lost connection to server!")
            self.close()
        else:
            self.database.save_message(
                message_type=MessageType.outcome,
                contact=self.current_chat,
                message=message_text,
            )
            logger.debug(f"Message sent to {self.current_chat}: {message_text}")
            self.history_list_update()

    @pyqtSlot(str)
    def message(self, sender):
        if sender == self.current_chat:
            self.history_list_update()
        else:
            if self.database.check_contact(sender):
                if (
                    self.messages.question(
                        self,
                        "New message",
                        f"Receive new message from {sender}, start new chat?",
                        QMessageBox.Yes,
                        QMessageBox.No,
                    )
                    == QMessageBox.StandardButton.Yes
                ):
                    self.current_chat = sender
                    self.set_active_user()
            else:
                if (
                    self.messages.question(
                        self,
                        "New message",
                        f"Receive new message from {sender}.\nHe is not in contacts.\n"
                        f"Add him to contacts and start new chat?",
                        QMessageBox.StandardButton.Yes,
                        QMessageBox.StandardButton.No,
                    )
                    == QMessageBox.StandardButton.Yes
                ):
                    self.add_contact(sender)
                    self.current_chat = sender
                    self.set_active_user()

    @pyqtSlot()
    def connection_lost(self):
        self.messages.warning(self, "Error", "Lost connection to server!")
        self.close()

    def make_connection(self, client):
        client.new_message.connect(self.message)
        client.connection_lost.connect(self.connection_lost)
