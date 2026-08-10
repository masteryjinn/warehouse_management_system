from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox, QGridLayout
)
from PyQt6.QtCore import Qt
from utils.load_styles import load_dialog_styles
import re


class EmployeeFormDialog(QDialog):
    def __init__(self, employee=None):
        super().__init__()
        self.employee = employee
        self.init_ui()

    def init_ui(self):
        title_text = "Редагування працівника" if self.employee else "Додавання працівника"
        self.setWindowTitle(f"👤 {title_text}")
        self.setFixedSize(450, 400)
        self.setStyleSheet(load_dialog_styles())
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel(f"📝 {title_text}")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; color: #1b263b; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Сітка вводу даних
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1) # Поля вводу будуть займати весь вільний простір

        # ПІБ
        grid.addWidget(QLabel("<b>ПІБ:</b>"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Прізвище, Ім’я, По батькові")
        grid.addWidget(self.name_input, 0, 1)

        # Посада
        grid.addWidget(QLabel("<b>Посада:</b>"), 1, 0)
        self.position_input = QLineEdit()
        self.position_input.setPlaceholderText("Напр: Менеджер складу")
        grid.addWidget(self.position_input, 1, 1)

        # Телефон
        grid.addWidget(QLabel("<b>Телефон:</b>"), 2, 0)
        self.phone_input = QLineEdit()
        # Твоя маска, але в більш читабельному форматі
        self.phone_input.setInputMask("+380999999999;_") 
        self.phone_input.setPlaceholderText("+380_________")
        grid.addWidget(self.phone_input, 2, 1)

        # Email
        grid.addWidget(QLabel("<b>Email:</b>"), 3, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("worker@company.com")
        grid.addWidget(self.email_input, 3, 1)

        # Адреса
        grid.addWidget(QLabel("<b>Адреса:</b>"), 4, 0)
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Місто, вул., буд.")
        grid.addWidget(self.address_input, 4, 1)

        main_layout.addLayout(grid)
        main_layout.addStretch() # Відсуваємо кнопки до низу

        # Кнопки дії
        button_layout = QHBoxLayout()
        btn_action_text = "💾 Оновити дані" if self.employee else "✅ Додати до штату"
        self.save_button = QPushButton(btn_action_text)
        self.cancel_button = QPushButton("✖️ Скасувати")

        # Стилізуємо кнопки в загальному стилі системи
        self.save_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold; padding: 10px;")
        self.cancel_button.setStyleSheet("background-color: #f0f3f5; color: #5d6d7e; border: 1px solid #d1d9e6; padding: 10px;")

        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Логіка сигналів
        self.save_button.clicked.connect(self.accept_with_validation)
        self.cancel_button.clicked.connect(self.reject)

        # Заповнення даними
        if self.employee:
            self.populate_fields()

    def populate_fields(self):
        self.name_input.setText(self.employee.get("name", ""))
        self.position_input.setText(self.employee.get("position", ""))
        self.phone_input.setText(self.employee.get("phone", ""))
        self.email_input.setText(self.employee.get("email", ""))
        self.address_input.setText(self.employee.get("address", ""))

    def accept_with_validation(self):
        name = self.name_input.text().strip()
        position = self.position_input.text().strip()
        raw_phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        # Перевірка імені та посади
        if not name:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть ім’я працівника.")
            return
        if not position:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть посаду.")
            return

        phone_raw = self.phone_input.text()
        # Перевіряємо, чи немає в рядку підкреслень (якщо маска не заповнена до кінця)
        if "_" in phone_raw or len(phone_raw) < 13:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть повний номер телефону.")
            return

        # Перевірка email
        if not email:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть email.")
            return
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            QMessageBox.warning(self, "Помилка", "Невірний формат email.")
            return
        # Перевірка адреси
        address = self.address_input.text().strip() 
        if not address:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть адресу.")
            return

        self.accept()

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "position": self.position_input.text(),
            "contacts": {
                "phone": self.phone_input.text(),
                "email": self.email_input.text(),
                "address": self.address_input.text()
            }
        }
