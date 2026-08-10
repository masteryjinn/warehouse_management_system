from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QMessageBox, QCheckBox, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import Qt

from user_session.current_user import CurrentUser
import requests
from services.signals import AppSignals
from config.config import API_URL
import re

class ChangePasswordTab(QWidget):
    def __init__(self, is_temp_password=False):
        super().__init__()
        self.is_temp_password = is_temp_password
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🔐 Зміна пароля — WMS")
        self.setStyleSheet("""
            QWidget {
                background-color: #ffffff;
                color: #2c3e50;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }

            QLabel {
                font-size: 15px;
                font-weight: bold;
                color: #1b263b;
            }

            QLineEdit {
                background-color: #f5faff;
                border: 1px solid #d1d9e6;
                padding: 10px;
                font-size: 15px;
                font-weight: bold; /* Жирний шрифт для вводу */
                border-radius: 8px;
                color: #1b263b;
            }

            QLineEdit:focus {
                background-color: #ffffff;
                border: 2px solid #3498db;
            }

            /* Стилізація чекбоксів, щоб їх було видно на білому */
            QCheckBox {
                font-size: 13px;
                color: #415a77;
                padding: 4px 0px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border: 2px solid #3498db;
                border-radius: 4px;
                background-color: #fff;
            }
            QCheckBox::indicator:checked {
                background-color: #3498db;
                border: 2px solid #2980b9;
            }

            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 8px;
                min-width: 150px;
                border: none;
            }

            QPushButton:hover {
                background-color: #2980b9;
            }
        """)

        self.setContentsMargins(25, 25, 25, 25)
        self.setFixedSize(380, 500 if self.is_temp_password else 450)  

        main_layout = QVBoxLayout()
        main_layout.setSpacing(12)

        # Заголовок
        title_label = QLabel("Оновлення безпеки")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; color: #1b263b; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        if self.is_temp_password:
            info_label = QLabel(
                "⚠️ Ви використовуєте тимчасовий пароль.\n"
                "Його необхідно змінити для безпеки."
            )
            info_label.setStyleSheet("color: #d32f2f; font-weight: normal; font-size: 13px;")
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            main_layout.addWidget(info_label)

        # Поля
        self.new_password_input = QLineEdit()
        self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.new_password_input.setPlaceholderText("Новий пароль")
        # Перехід на наступне поле по Enter
        self.new_password_input.returnPressed.connect(lambda: self.confirm_password_input.setFocus())

        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setPlaceholderText("Підтвердіть пароль")
        # Сабміт по Enter на другому полі
        self.confirm_password_input.returnPressed.connect(self.change_password)

        self.show_new_password_checkbox = QCheckBox('Показати пароль')
        self.show_confirm_password_checkbox = QCheckBox('Показати підтвердження')

        # Підключення видимості
        self.show_new_password_checkbox.stateChanged.connect(self.toggle_new_password_visibility)
        self.show_confirm_password_checkbox.stateChanged.connect(self.toggle_confirm_password_visibility)

        # 1. Створюємо мітку надійності
        self.password_strength_label = QLabel("Надійність: —")
        self.password_strength_label.setStyleSheet("font-size: 12px; font-weight: normal; color: #7f8c8d; margin-top: -5px;")
        
        # 2. Підключаємо сигнал перевірки (не забудь додати метод check_password_strength нижче в класі)
        self.new_password_input.textChanged.connect(self.check_password_strength)

        # 3. Компонування полів у main_layout (У ПРАВИЛЬНОМУ ПОРЯДКУ)
        main_layout.addWidget(QLabel("Новий пароль"))
        main_layout.addWidget(self.new_password_input)
        
        # Вставляємо надійність ПІСЛЯ поля, але ПЕРЕД чекбоксом
        main_layout.addWidget(self.password_strength_label) 
        
        main_layout.addWidget(self.show_new_password_checkbox)

        main_layout.addSpacing(10)

        main_layout.addWidget(QLabel("Підтвердження пароля"))
        main_layout.addWidget(self.confirm_password_input)
        main_layout.addWidget(self.show_confirm_password_checkbox)

        main_layout.addStretch()

        # Кнопка збереження
        self.change_btn = QPushButton("💾 Зберегти пароль")
        self.change_btn.clicked.connect(self.change_password)
        # Прибрали self.change_btn.setCursor, бо ти хотіла чистий стиль без "руки"
        
        main_layout.addWidget(self.change_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(main_layout)

    def closeEvent(self, event):
        if self.is_temp_password:
            QMessageBox.warning(
                self,
                "Зміна пароля обов’язкова",
                "Ви використовуєте тимчасовий пароль.\nДля продовження потрібно задати новий постійний пароль."
            )
            event.ignore()
        else:
            event.accept()

    def check_password_strength(self, password):
        if not password:
            self.password_strength_label.setText("Надійність: —")
            self.password_strength_label.setStyleSheet("color: #7f8c8d;")
            return

        # Проста логіка оцінки
        has_upper = any(c.isupper() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_spec = any(c in "!@#$%^&*" for c in password)
        length = len(password)

        if length < 6:
            score = "Слабкий ❌"
            color = "#e74c3c" # Червоний
        elif length < 10 or not (has_upper and has_digit):
            score = "Середній ⚠️"
            color = "#f39c12" # Помаранчевий
        else:
            score = "Надійний ✅"
            color = "#27ae60" # Зелений

        self.password_strength_label.setText(f"Надійність: {score}")
        self.password_strength_label.setStyleSheet(f"color: {color}; font-size: 12px; font-weight: bold;")

    def toggle_new_password_visibility(self):
        if self.show_new_password_checkbox.isChecked():
            self.new_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.new_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def toggle_confirm_password_visibility(self):
        if self.show_confirm_password_checkbox.isChecked():
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def change_password(self):
        new_password = self.new_password_input.text()
        confirm_password = self.confirm_password_input.text()

        if new_password != confirm_password:
            self.show_error("Новий пароль та підтвердження не співпадають.")
            return

        if not self.is_valid_password(new_password):
            self.show_error("Пароль повинен містити латинські літери, цифру та бути довшим за 8 символів.")
            return

        current_user = CurrentUser()
        token = current_user.get_token()
        is_temp_password = current_user.get_is_temp_password()

        try:
            if is_temp_password == 1:
                # Зміна тимчасового пароля (без токена)
                user_id = current_user.get_user_id()
                response = requests.post(
                    f"{API_URL}/change-password-after-reset/",
                    json={"user_id": user_id, "new_password": new_password}
                )
                if response.status_code == 200:
                    data = response.json()
                    token = data.get("token")
                    if token:
                        current_user.set_token(token)
                    current_user.password_is_changed()
                    self.is_temp_password = False
                    QMessageBox.information(self, "Успіх", "Пароль успішно змінено!")
                    self.close()  # Закриваємо вікно зміни пароля
                else:
                    error_message = response.json().get("detail", "Невідома помилка.")
                    self.show_error(f"Помилка: {error_message}")

            elif token and is_temp_password == 0:
                # Звичайна зміна пароля (з токеном)
                response = requests.post(
                    f"{API_URL}/change-password/",
                    json={"new_password": new_password},
                    headers={"Authorization": f"Bearer {token}"}
                )
                if response.status_code == 200:
                    QMessageBox.information(self, "Успіх", "Пароль успішно змінено!")
                    self.close()
                elif response.status_code == 401:
                    self.show_error("Токен недійсний або прострочений. Будь ласка, увійдіть знову.")
                    self.close()
                    AppSignals.get_instance().logout_requested.emit()
                else:
                    error_message = response.json().get("detail", "Невідома помилка.")
                    self.show_error(f"Помилка: {error_message}")
            else:
                self.show_error("Помилка авторизації. Будь ласка, увійдіть знову.")
                self.close()
                AppSignals.get_instance().logout_requested.emit()

        except requests.exceptions.RequestException as e:
            self.show_error(f"Помилка мережі: {e}")


    def is_valid_password(self, password):
        password_regex = r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$"
        return re.match(password_regex, password) is not None

    def show_error(self, message):
        QMessageBox.critical(self, 'Помилка', message)

    def show_message(self, message):
        QMessageBox.information(self, 'Успіх', message)
