from PyQt6.QtWidgets import (QApplication, QDialog, QLabel, QLineEdit,
                             QPushButton)


class AuthErrorDialog(QDialog):
    def __init__(self, error_text):
        super().__init__()

        self.ok_pressed = False

        self.setWindowTitle("Auth error!")
        self.setFixedSize(200, 50)

        self.label = QLabel(error_text, self)
        self.label.move(20, 20)
        self.label.setFixedSize(150, 10)

        self.show()
