import sys
from typing import Generator

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import (QApplication, QDialog, QFileDialog, QLabel,
                             QLineEdit, QMainWindow, QPushButton, QTableView)


def create_active_clients_table(statistics: Generator):
    lst = QStandardItemModel()
    lst.setHorizontalHeaderLabels(
        ["Login", "IP", "Port", "Sent messages", "Recieved messages"]
    )
    for login, ip, port, msg_sent, msg_rcvd in statistics:
        login = QStandardItem(login)
        login.setEditable(False)
        ip = QStandardItem(ip)
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        msg_sent = QStandardItem(str(msg_sent))
        msg_sent.setEditable(False)
        msg_rcvd = QStandardItem(str(msg_rcvd))
        msg_rcvd.setEditable(False)
        lst.appendRow([login, ip, port, msg_sent, msg_rcvd])
    return lst


def create_clients_table(client_list: Generator):
    lst = QStandardItemModel()
    lst.setHorizontalHeaderLabels(["Login", "Last seen", "Last IP", "Last port"])
    for login, last_seen, ip, port in client_list:
        login = QStandardItem(login)
        login.setEditable(False)
        last_seen = QStandardItem(str(last_seen))
        last_seen.setEditable(False)
        ip = QStandardItem(str(ip))
        ip.setEditable(False)
        port = QStandardItem(str(port))
        port.setEditable(False)
        lst.appendRow([login, last_seen, ip, port])
    return lst


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        exitAction = QAction("Exit", self)
        exitAction.setShortcut("Ctrl+Q")
        exitAction.triggered.connect(QApplication.instance().quit)

        self.refresh_button = QAction("Refresh", self)

        self.config_btn = QAction("Config", self)

        self.show_all_clients_button = QAction("Clients", self)

        self.statusBar()

        self.toolbar = self.addToolBar("MainBar")
        self.toolbar.addAction(exitAction)
        self.toolbar.addAction(self.refresh_button)
        self.toolbar.addAction(self.show_all_clients_button)
        self.toolbar.addAction(self.config_btn)

        self.setFixedSize(800, 600)
        self.setWindowTitle("Messaging Server alpha release")

        self.label = QLabel("Connected clients:", self)
        self.label.setFixedSize(240, 15)
        self.label.move(10, 25)

        self.active_clients_table = QTableView(self)
        self.active_clients_table.move(10, 45)
        self.active_clients_table.setFixedSize(780, 400)

        self.show()


class ClientsWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Clients")
        self.setFixedSize(600, 700)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        self.close_button = QPushButton("Close", self)
        self.close_button.move(250, 650)
        self.close_button.clicked.connect(self.close)

        self.clients_table = QTableView(self)
        self.clients_table.move(10, 10)
        self.clients_table.setFixedSize(580, 620)

        self.show()


class ConfigWindow(QDialog):
    def __init__(self):
        super().__init__()

        self.setFixedSize(365, 260)
        self.setWindowTitle("Настройки сервера")

        self.db_path_label = QLabel("Путь до файла базы данных: ", self)
        self.db_path_label.move(10, 10)
        self.db_path_label.setFixedSize(240, 15)

        self.db_path = QLineEdit(self)
        self.db_path.setFixedSize(250, 20)
        self.db_path.move(10, 30)
        self.db_path.setReadOnly(True)

        self.db_path_select = QPushButton("Обзор...", self)
        self.db_path_select.move(275, 28)

        self.db_path_select.clicked.connect(self._open_file_dialog)

        self.db_file_label = QLabel("Имя файла базы данных: ", self)
        self.db_file_label.move(10, 68)
        self.db_file_label.setFixedSize(180, 15)

        self.db_file = QLineEdit(self)
        self.db_file.move(200, 66)
        self.db_file.setFixedSize(150, 20)

        self.port_label = QLabel("Номер порта для соединений:", self)
        self.port_label.move(10, 108)
        self.port_label.setFixedSize(180, 15)

        self.port = QLineEdit(self)
        self.port.move(200, 108)
        self.port.setFixedSize(150, 20)

        self.ip_label = QLabel("С какого IP принимаем соединения:", self)
        self.ip_label.move(10, 148)
        self.ip_label.setFixedSize(180, 15)

        self.ip_label_note = QLabel(
            " оставьте это поле пустым, чтобы\n принимать соединения с любых адресов.",
            self,
        )
        self.ip_label_note.move(10, 168)
        self.ip_label_note.setFixedSize(500, 30)

        self.ip = QLineEdit(self)
        self.ip.move(200, 148)
        self.ip.setFixedSize(150, 20)

        self.save_btn = QPushButton("Сохранить", self)
        self.save_btn.move(190, 220)

        self.close_button = QPushButton("Закрыть", self)
        self.close_button.move(275, 220)
        self.close_button.clicked.connect(self.close)

        self.show()

    def _open_file_dialog(self):
        global dialog
        dialog = QFileDialog(self)
        path = dialog.getExistingDirectory()
        path = path.replace("/", "\\")
        self.db_path.insert(path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    sys.exit(app.exec())
