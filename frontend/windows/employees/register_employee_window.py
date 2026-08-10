from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QMessageBox, QApplication,
    QCheckBox, QGridLayout
)
from PyQt6.QtCore import Qt
import random, string
import re
from utils.load_styles import load_dialog_styles

class RegisterEmployeeWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.payload = {}

        self.setWindowTitle("Реєстрація працівника")
        self.setStyleSheet(load_dialog_styles())
        self.setMinimumSize(380, 500)
        self.init_ui()

    def _create_input(self, label, is_password=False):
        """Допоміжний метод для створення полів вводу"""
        self.layout().addWidget(QLabel(label))
        edit = QLineEdit()
        if is_password:
            edit.setEchoMode(QLineEdit.EchoMode.Password)
        self.layout().addWidget(edit)
        return edit

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Заголовок
        title = QLabel("🔐 Реєстрація нового акаунту")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1b263b; padding-bottom: 10px;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Сітка для полів
        grid = QGridLayout()
        grid.setSpacing(10)

        # Логін
        grid.addWidget(QLabel("<b>Логін:</b>"), 0, 0)
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Наприклад: i_ivanov")
        grid.addWidget(self.username_input, 0, 1)

        # Пароль
        grid.addWidget(QLabel("<b>Пароль:</b>"), 1, 0)
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Мінімум 8 символів")
        grid.addWidget(self.password_input, 1, 1)

        # Підтвердження
        grid.addWidget(QLabel("<b>Повтор:</b>"), 2, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        grid.addWidget(self.confirm_password_input, 2, 1)

        # Роль
        grid.addWidget(QLabel("<b>Роль:</b>"), 3, 0)
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Адмін", "Менеджер", "Звичайний працівник"])
        grid.addWidget(self.role_combo, 3, 1)

        layout.addLayout(grid)

        # Блок керування паролем (компактний)
        pwd_manage_layout = QHBoxLayout()
        self.show_password_checkbox = QCheckBox("Показати символи")
        gen_btn = QPushButton("🎲 Згенерувати")
        gen_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        gen_btn.setStyleSheet("background-color: #f0f3f5; border: 1px solid #d1d9e6; padding: 5px 10px;")
        
        pwd_manage_layout.addWidget(self.show_password_checkbox)
        pwd_manage_layout.addStretch()
        pwd_manage_layout.addWidget(gen_btn)
        layout.addLayout(pwd_manage_layout)

        # Статус валідації (один рядок замість двох)
        self.status_label = QLabel("Заповніть усі поля")
        self.status_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        # Кнопки дій
        actions = QHBoxLayout()
        self.reg_btn = QPushButton(" 📥 Створити акаунт")
        self.reg_btn.setStyleSheet("background-color: #2ecc71; color: white; font-weight: bold; padding: 12px;")
        
        can_btn = QPushButton("✖️ Скасувати")
        can_btn.setObjectName("cancel_button")
        can_btn.setStyleSheet("padding: 12px;")

        actions.addWidget(self.reg_btn)
        actions.addWidget(can_btn)
        layout.addLayout(actions)

        # Зв'язки
        gen_btn.clicked.connect(self.generate_random_password)
        self.show_password_checkbox.stateChanged.connect(self.toggle_password_visibility_checkbox)
        self.password_input.textChanged.connect(self.validate_all)
        self.confirm_password_input.textChanged.connect(self.validate_all)
        self.reg_btn.clicked.connect(self.register_user)
        can_btn.clicked.connect(self.reject)

    def toggle_password_visibility_checkbox(self):
        is_checked = self.show_password_checkbox.isChecked()
        mode = QLineEdit.EchoMode.Normal if is_checked else QLineEdit.EchoMode.Password
        self.password_input.setEchoMode(mode)
        self.confirm_password_input.setEchoMode(mode)

    def generate_random_password(self):
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        self.password_input.setText(pwd)
        self.confirm_password_input.setText(pwd)
        QApplication.clipboard().setText(pwd)

    def _update_style(self, widget, is_valid):
        widget.setProperty("valid", is_valid)
        widget.style().unpolish(widget)
        widget.style().polish(widget)

    def validate_all(self):
        pwd = self.password_input.text()
        conf = self.confirm_password_input.text()
        
        # Критерії
        has_len = len(pwd) >= 8
        has_digit = any(c.isdigit() for c in pwd)
        has_alpha = any(c.isalpha() for c in pwd)
        is_pwd_ok = has_len and has_digit and has_alpha
        is_match = (pwd == conf and conf != "")

        # Стиль для основного пароля
        if not pwd:
            self.password_input.setStyleSheet("")
        elif is_pwd_ok:
            self.password_input.setStyleSheet("border: 2px solid #2ecc71; background-color: #f0fff4;")
        else:
            self.password_input.setStyleSheet("border: 2px solid #e74c3c; background-color: #fff5f5;")

        # Стиль для підтвердження
        if not conf:
            self.confirm_password_input.setStyleSheet("")
        elif is_match:
            self.confirm_password_input.setStyleSheet("border: 2px solid #2ecc71; background-color: #f0fff4;")
        else:
            self.confirm_password_input.setStyleSheet("border: 2px solid #e74c3c; background-color: #fff5f5;")

        # Оновлення загального тексту
        if not is_pwd_ok and pwd:
            self.status_label.setText("❌ Пароль занадто простий")
            self.status_label.setStyleSheet("color: #e74c3c;")
        elif not is_match and conf:
            self.status_label.setText("❌ Паролі не збігаються")
            self.status_label.setStyleSheet("color: #e74c3c;")
        elif is_pwd_ok and is_match:
            self.status_label.setText("✅ Все чудово")
            self.status_label.setStyleSheet("color: #2ecc71;")
        
        return is_pwd_ok and is_match

    def register_user(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()

        # 1. Базова перевірка на пусті поля
        if not username or not password:
            return QMessageBox.warning(self, "Помилка", "Логін та пароль не можуть бути порожніми.")

        # 2. Перевірка довжини логіна (наприклад, мінімум 3 символи)
        if len(username) < 3:
            return QMessageBox.warning(self, "Помилка", "Логін має містити не менше 3-х символів.")

        # 3. Перевірка на пробіли всередині логіна
        if " " in username:
            return QMessageBox.warning(self, "Помилка", "Логін не може містити пробіли.")

        # 4. Перевірка на спеціальні символи (тільки латиниця, цифри та підкреслення)
        # Це важливо, щоб уникнути помилок у базі або проблем з кодуванням
        if not re.match(r"^[a-zA-Z0-9_]+$", username):
            return QMessageBox.warning(
                self, "Помилка", "Логін може містити лише латинські літери, цифри та символ підкреслення (_)."
            )

        # 5. Ваша стандартна валідація (наприклад, для пароля)
        if not self.validate_all():
            return QMessageBox.warning(self, "Помилка", "Будь ласка, виправте помилки у полях.")

        role_map = {"Адмін": "admin", "Менеджер": "manager", "Звичайний працівник": "employee"}
        
        self.payload = {
            "username": username,
            "password": password,
            "role": role_map.get(self.role_combo.currentText())
        }  
        self.accept()

    def get_registration_payload(self):
        return self.payload