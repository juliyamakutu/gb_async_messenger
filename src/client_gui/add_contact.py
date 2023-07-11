import sys

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QComboBox, QDialog, QLabel, QPushButton

sys.path.append("../")


class AddContactDialog(QDialog):
    def __init__(self, client, database):
        super().__init__()
        self.client = client
        self.database = database

        self.setFixedSize(350, 120)
        self.setWindowTitle("Select contact name:")
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        self.setModal(True)

        self.selector_label = QLabel("Select contact name:", self)
        self.selector_label.setFixedSize(200, 20)
        self.selector_label.move(10, 0)

        self.selector = QComboBox(self)
        self.selector.setFixedSize(200, 20)
        self.selector.move(10, 30)

        self.btn_refresh = QPushButton("Refresh", self)
        self.btn_refresh.setFixedSize(100, 30)
        self.btn_refresh.move(60, 60)

        self.btn_ok = QPushButton("Add", self)
        self.btn_ok.setFixedSize(100, 30)
        self.btn_ok.move(230, 20)

        self.btn_cancel = QPushButton("Cancel", self)
        self.btn_cancel.setFixedSize(100, 30)
        self.btn_cancel.move(230, 60)
        self.btn_cancel.clicked.connect(self.close)

        self.possible_contacts_update()
        self.btn_refresh.clicked.connect(self.possible_contacts_update)

    def possible_contacts_update(self):
        self.selector.clear()
        contacts_list = set(self.database.get_contacts())
        users_list = set(self.client.get_users())
        users_list.remove(self.client.account_name)
        self.selector.addItems(users_list - contacts_list)
