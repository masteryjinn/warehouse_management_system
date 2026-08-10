from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QGridLayout,
    QPushButton, QComboBox, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
import re
from utils.load_styles import load_dialog_styles

class CustomerDialog(QDialog):
    def __init__(self, customer=None):
        super().__init__()
        self.customer = customer
        self.setWindowTitle("Редагування клієнта" if customer else "Додавання клієнта")
        self.setFixedSize(450, 400)
        self.setStyleSheet(load_dialog_styles())
        self.init_ui()

    def init_ui(self):
        # Встановлюємо заголовок вікна залежно від режиму
        self.setWindowTitle("👤 Клієнт" if self.customer else "➕ Новий клієнт")
        self.setStyleSheet(load_dialog_styles())
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # Заголовок усередині вікна
        title_text = "📝 Редагування даних" if self.customer else "🆕 Реєстрація клієнта"
        title_label = QLabel(title_text)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; color: #1b263b; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Сітка вводу
        grid = QGridLayout()
        grid.setSpacing(10)

        # Ім’я
        grid.addWidget(QLabel("<b>Ім’я / Назва:</b>"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("ПІБ або назва компанії")
        grid.addWidget(self.name_input, 0, 1)

        # Тип клієнта
        grid.addWidget(QLabel("<b>Тип:</b>"), 1, 0)
        self.type_input = QComboBox()
        self.type_input.addItems(["Фізична особа", "Юридична особа"])
        self.type_input.setItemData(0, "individual", Qt.ItemDataRole.UserRole)  # Фізична особа
        self.type_input.setItemData(1, "business", Qt.ItemDataRole.UserRole)  # Юридична особа
        grid.addWidget(self.type_input, 1, 1)

        # Телефон (з твоєю маскою)
        grid.addWidget(QLabel("<b>Телефон:</b>"), 2, 0)
        self.phone_input = QLineEdit()
        self.phone_input.setInputMask("+380999999999;_") 
        self.phone_input.setPlaceholderText("+380_________")
        grid.addWidget(self.phone_input, 2, 1)

        # Email
        grid.addWidget(QLabel("<b>E-mail:</b>"), 3, 0)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("example@mail.com")
        grid.addWidget(self.email_input, 3, 1)

        # Адреса
        grid.addWidget(QLabel("<b>Адреса:</b>"), 4, 0)
        self.address_input = QLineEdit()
        self.address_input.setPlaceholderText("Вулиця, номер будинку, місто")
        grid.addWidget(self.address_input, 4, 1)

        main_layout.addLayout(grid)

        # Логіка переходу по Enter для UX
        self.name_input.returnPressed.connect(lambda: self.phone_input.setFocus())
        self.email_input.returnPressed.connect(lambda: self.address_input.setFocus())
        self.address_input.returnPressed.connect(self.accept_with_validation)

        # Кнопки
        button_layout = QHBoxLayout()
        btn_text = "💾 Оновити" if self.customer else "✅ Додати клієнта"
        self.save_button = QPushButton(btn_text)
        self.cancel_button = QPushButton("✖️ Скасувати")
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Зв'язки
        self.save_button.clicked.connect(self.accept_with_validation)
        self.cancel_button.clicked.connect(self.reject)

        if self.customer:
            self.populate_fields()

    def populate_fields(self):
        self.name_input.setText(self.customer.get("name", ""))
        self.type_input.setCurrentIndex(self.type_input.findData(self.customer.get("type", "individual")))
        self.phone_input.setText(self.customer.get("phone", ""))
        self.email_input.setText(self.customer.get("email", ""))
        self.address_input.setText(self.customer.get("address", ""))

    def accept_with_validation(self):
        name = self.name_input.text().strip()
        raw_phone = self.phone_input.text().strip()
        email = self.email_input.text().strip()

        # Ім’я (обов’язково)
        if not name:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть ім’я клієнта.")
            return
        
        if "_" in raw_phone or len(raw_phone) < 13:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть повний номер телефону.")
            return

        # Email (опціонально, але якщо вказано — перевіряємо формат)
        if email and not re.match(r'^[\w\.-]+@[\w\.-]+\.\w{2,}$', email):
            QMessageBox.warning(self, "Помилка", "Невірний формат email.")
            return

        self.accept()  # Усе добре — приймаємо форму

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "type": self.type_input.currentData(Qt.ItemDataRole.UserRole),
            "contacts": {
                "phone": self.phone_input.text(),
                "email": self.email_input.text(),
                "address": self.address_input.text()
            }
        }
