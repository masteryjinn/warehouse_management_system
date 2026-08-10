import re
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QMessageBox


class EmailInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔑 Відновлення пароля") # Додаємо емодзі для стилю
        self.setFixedSize(360, 180) # Трохи збільшили для кращих відступів

        # Використовуємо вже знайому логіку стилів
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-weight: bold;
                font-size: 14px;
                color: #1b263b;
                margin-bottom: 2px;
            }
            QLineEdit {
                background-color: #f5faff;
                padding: 10px;
                border: 1px solid #d1d9e6;
                border-radius: 8px;
                color: #1b263b;
                font-size: 15px;
                font-weight: bold; /* Робимо ввід жирним, як ти й хотіла */
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #ffffff;
            }
            QPushButton {
                padding: 10px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)

        self.label = QLabel("Введіть ваш e-mail:")
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@mail.com")
        
        # Перехід/підтвердження по Enter
        self.email_input.returnPressed.connect(self.validate_and_accept)

        layout.addWidget(self.label)
        layout.addWidget(self.email_input)

        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("Надіслати") 
        self.cancel_button = QPushButton("Скасувати")
        
        self.ok_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

        # Стилізуємо кнопки індивідуально через кольори
        self.ok_button.setStyleSheet("""
            background-color: #3498db;
            color: white;
        """)

        self.cancel_button.setStyleSheet("""
            background-color: #f0f3f5;
            color: #5d6d7e;
            border: 1px solid #d1d9e6;
        """)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def get_email(self):
        return self.email_input.text().strip()

    def validate_and_accept(self):
        email = self.get_email()
        if self.is_valid_email(email):
            self.accept()
        else:
            QMessageBox.warning(self, "Невірний email", "Будь ласка, введіть коректну електронну адресу.")

    def is_valid_email(self, email: str) -> bool:
        """Проста перевірка email за допомогою regex"""
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        return re.match(pattern, email) is not None
