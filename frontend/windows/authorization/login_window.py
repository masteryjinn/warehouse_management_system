import requests 
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QMessageBox, QCheckBox
)
from tabs.main_window import MainWindow
from user_session.current_user import CurrentUser
from PyQt6.QtGui import QGuiApplication
from PyQt6.QtCore import QRect
from windows.authorization.email_input_dialog import EmailInputDialog
from config.config import API_URL

class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('🔐 Авторизація — WMS') # Додаємо іконку в заголовок
        self.setFixedSize(330, 360) # Трохи збільшили висоту для вільного простору

        # Центруємо вікно на екрані
        screen = QGuiApplication.primaryScreen()
        screen_geometry: QRect = screen.availableGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                outline: none;
            }

            QLabel {
                font-weight: bold;
                font-size: 15px;
                color: #1b263b;
            }

            QLineEdit {
                background-color: #f5faff;
                padding: 10px;
                border: 1px solid #d1d9e6;
                border-radius: 8px;
                color: #1b263b;
                font-size: 15px;
                font-weight: bold;
            }

            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid #3498db;
            }

            /* Головна кнопка */
            QPushButton#login_btn {
                background-color: #3498db;
                color: white;
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-weight: bold;
                font-size: 15px;
            }

            QPushButton#login_btn:hover {
                background-color: #2980b9;
            }

            /* Кнопка "Забули пароль" як посилання */
            QPushButton#forgot_btn {
                background-color: transparent;
                color: #5d6d7e;
                border: none;
                font-weight: normal;
                font-size: 13px;
                text-decoration: underline;
            }

            QPushButton#forgot_btn:hover {
                color: #3498db;
            }
            QCheckBox {
                spacing: 8px; /* Відступ між квадратиком і текстом */
                color: #415a77;
            }

            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3498db; /* Синя рамка, яку точно видно */
                border-radius: 4px;
                background-color: #ffffff;
            }

            QCheckBox::indicator:hover {
                background-color: #f0faff;
                border: 2px solid #2980b9;
            }

            QCheckBox::indicator:checked {
                background-color: #3498db; /* Заливка при виборі */
                image: url(no_image); /* Очищуємо дефолтну галку, якщо вона глючить */
            }

            /* Малюємо білу галку через border для універсальності */
            QCheckBox::indicator:checked {
                background-color: #3498db;
                /* Можна додати іконку або просто залишати кольоровим */
            }
            QLineEdit:hover {
                border: 1px solid #3498db;
            }
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(35, 30, 35, 30)
        main_layout.setSpacing(12)

        # Ім'я користувача
        self.username_label = QLabel("Ім'я користувача")
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Введіть логін...")
        self.username_input.setMaxLength(30) # Обмеження для безпеки
        main_layout.addWidget(self.username_label)
        main_layout.addWidget(self.username_input)
        
        # Пароль
        self.password_label = QLabel('Пароль')
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("••••••••")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        main_layout.addWidget(self.password_label)
        main_layout.addWidget(self.password_input)

        # Чекбокс
        self.show_password_checkbox = QCheckBox('Показати пароль')
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility)
        main_layout.addWidget(self.show_password_checkbox)

        # Відступ перед кнопками
        main_layout.addStretch()

        # Кнопка Увійти
        self.login_button = QPushButton('🚀 Увійти')
        self.login_button.setObjectName("login_btn") # Для стилів
        self.login_button.clicked.connect(self.login)
        main_layout.addWidget(self.login_button)

        # Кнопка Забули пароль
        self.forgot_password_button = QPushButton('Забули пароль?')
        self.forgot_password_button.setObjectName("forgot_btn") # Для стилів
        self.forgot_password_button.clicked.connect(self.forgot_password)
        main_layout.addWidget(self.forgot_password_button)

        self.username_input.returnPressed.connect(self.focus_password) # Після Enter в логіні переходимо до пароля
        self.password_input.returnPressed.connect(self.login) # Після Enter в паролі намагаємося увійти

        self.setLayout(main_layout)

    def focus_password(self):
        """Переміщаємо фокус на поле пароля після Enter в логіні"""
        self.password_input.setFocus()

    def toggle_password_visibility(self):
        if self.show_password_checkbox.isChecked():
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def login(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            self.show_error("Будь ласка, введіть ім'я користувача та пароль!")
            return

        try:
            response = requests.post(f"{API_URL}/login/", json={"username": username, "password": password})

            if response.status_code == 200:
                data = response.json()
                user_id = data["user_id"]
                name = data["name"]
                token = data["token"]
                role = data["role"]
                is_temp_password = data["is_temp_password"]

                if is_temp_password:
                    QMessageBox.warning(self, "Попередження", "Ви використовуєте тимчасовий пароль. Будь ласка, змініть його.")

                current_user = CurrentUser()
                current_user.set_user_data(user_id, name, role, token, is_temp_password)

                self.username_input.clear()
                self.password_input.clear()

                self.show_main_app()

            else:
                try:
                    # Пробуємо отримати повідомлення з detail
                    error_message = response.json().get("detail", "Сталася помилка авторизації.")
                except Exception:
                    error_message = "Сталася помилка авторизації. Спробуйте пізніше."

                self.show_error(error_message)
                self.password_input.clear()

        except requests.RequestException as e:
            self.show_error(f"Помилка з'єднання з сервером: {e}")


    def forgot_password(self):
        dialog = EmailInputDialog(self)
        if dialog.exec():
            email = dialog.get_email().strip()
            if email:
                try:
                    response = requests.post(f"{API_URL}/reset-password/", json={"email": email})

                    if response.status_code == 200:
                        data = response.json()
                        message = data.get("message", "Пароль скинуто. Перевірте пошту.")
                        QMessageBox.information(self, "Відновлення пароля", message)
                    else:
                        data = response.json()
                        error_msg = data.get("detail", "Помилка при відновленні пароля.")
                        self.show_error(error_msg)
                except requests.exceptions.RequestException:
                    self.show_error("Не вдалося підключитися до сервера.")
            else:
                self.show_error("Email не може бути порожнім.")

    def show_main_app(self):
        self.close()
        self.main_window = MainWindow(self)
        self.main_window.show()

    def show_error(self, message):
        QMessageBox.critical(self, 'Помилка', message)
