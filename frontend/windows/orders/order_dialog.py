from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QLineEdit, QMessageBox, QTextEdit
)
from PyQt6.QtCore import Qt
from windows.customers.customer_select_dialog import CustomerSelectDialog
from utils.load_styles import load_dialog_styles

class OrderDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛒 Нове замовлення")
        self.setFixedSize(420, 350)
        self.selected_customer = None
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_dialog_styles())

        self.setContentsMargins(20, 20, 20, 20)

        layout = QVBoxLayout()
        layout.setSpacing(10)

        title_label = QLabel("Створення замовлення")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; padding-bottom: 10px;")
        layout.addWidget(title_label)

        self.customer_label = QLabel("Клієнт:")
        layout.addWidget(self.customer_label)

        customer_box= QHBoxLayout()
        self.customer_input = QLineEdit()
        self.customer_input.setReadOnly(True)
        customer_box.addWidget(self.customer_input)

        # Кнопка вибору клієнта
        self.customer_button = QPushButton("🔍")
        self.customer_button.clicked.connect(self.open_customer_dialog)
        customer_box.addWidget(self.customer_button)
        layout.addLayout(customer_box)

        self.adress_label = QLabel("Адреса:")
        layout.addWidget(self.adress_label)

        # Замість QLineEdit використовуємо QTextEdit
        self.adress_input = QTextEdit() 
        self.adress_input.setReadOnly(True)
        self.adress_input.setMaximumHeight(80)  # Бажано обмежити висоту, щоб вікно не "попливло"
        self.adress_input.setPlaceholderText("Тут з'явиться адреса після вибору клієнта...")
        layout.addWidget(self.adress_input)

        # Кнопки
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("🛒 Додати товари")
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.cancel_button.setObjectName("cancel_button")
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.save_button.clicked.connect(self.accept_with_validation)
        self.cancel_button.clicked.connect(self.reject)

    def open_customer_dialog(self):
        dialog = CustomerSelectDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            customer = dialog.get_selected_customer()
            if customer:
                self.selected_customer = customer
                self.customer_input.setText(customer["name"])
                self.adress_input.setText(customer["address"])

    def accept_with_validation(self):
        if not self.selected_customer:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть клієнта.")
            return

        self.accept()

    def get_data(self):
        return {
            "customer_id": self.selected_customer["customer_id"] if self.selected_customer else None,
        }
