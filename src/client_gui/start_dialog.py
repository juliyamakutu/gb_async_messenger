from PyQt6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
                             QPushButton)


class UserNameDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle("Hello!")
        self.setFixedSize(175, 143)

        self.label = QLabel("Enter user name:", self)
        self.label.move(10, 10)
        self.label.setFixedSize(150, 10)

        self.client_name = QLineEdit(self)
        self.client_name.setFixedSize(154, 20)
        self.client_name.move(10, 30)

        self.label = QLabel("Enter password:", self)
        self.label.move(10, 60)
        self.label.setFixedSize(150, 10)

        self.client_pass = QLineEdit(self)
        self.client_pass.setFixedSize(154, 20)
        self.client_pass.setEchoMode(QLineEdit.EchoMode.Password)
        self.client_pass.move(10, 80)

        self.btn_ok = QPushButton("Start", self)
        self.btn_ok.move(10, 110)
        self.btn_ok.clicked.connect(self.click)

        self.btn_cancel = QPushButton("Exit", self)
        self.btn_cancel.move(90, 110)
        self.btn_cancel.clicked.connect(QApplication.instance().quit)

        self.show()

    def click(self):
        if self.client_name.text():
            self.ok_pressed = True
            QApplication.instance().quit()
