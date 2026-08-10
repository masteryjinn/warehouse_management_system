
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QGridLayout
from PyQt6.QtCore import Qt
from utils.load_styles import load_dialog_styles

class FilterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Фільтрація бази постачальників")
        self.setFixedSize(450, 400)
        self.current_filters = parent.__dict__  
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_dialog_styles()) 
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("Налаштування фільтрів")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; color: #1b263b; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Сітка для параметрів (Label | Input)
        grid = QGridLayout()
        grid.setSpacing(10)

        # ПІБ / Назва
        grid.addWidget(QLabel("Ім’я містить:"), 0, 0)
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введіть частину імені...")
        # Додаємо підтримку Enter для швидкого пошуку
        self.name_input.returnPressed.connect(self.accept)
        grid.addWidget(self.name_input, 0, 1)

        # Тип постачальника
        grid.addWidget(QLabel("Тип постачальника:"), 1, 0)
        self.type_input = QComboBox()
        self.type_input.addItems(["Будь-який", "Виробник", "Дистриб'ютор", "Оптовий продавець"])
        self.type_input.setItemData(0, "all", Qt.ItemDataRole.UserRole)  # Будь-який
        self.type_input.setItemData(1, "manufacturer", Qt.ItemDataRole.UserRole)  # Виробник
        self.type_input.setItemData(2, "distributor", Qt.ItemDataRole.UserRole,)  # Дистриб'ютор
        self.type_input.setItemData(3, "wholesaler", Qt.ItemDataRole.UserRole)  # Оптовий продавець
        grid.addWidget(self.type_input, 1, 1)

        # Чекбокси наявності (Email, Телефон, Адреса)
        grid.addWidget(QLabel("Електронна пошта:"), 2, 0)
        self.email_input = QComboBox()
        self.email_input.addItems(["Будь-яка", "З поштою", "Без пошти"])
        self.email_input.setItemData(0, "all", Qt.ItemDataRole.UserRole)
        self.email_input.setItemData(1, True, Qt.ItemDataRole.UserRole)
        self.email_input.setItemData(2, False, Qt.ItemDataRole.UserRole)
        grid.addWidget(self.email_input, 2, 1)

        # Номер телефону
        grid.addWidget(QLabel("Номер телефону:"), 3, 0)
        self.phone_input = QComboBox()
        self.phone_input.addItems(["Будь-який", "З телефоном", "Без телефону"])
        self.phone_input.setItemData(0, "all", Qt.ItemDataRole.UserRole)
        self.phone_input.setItemData(1, True, Qt.ItemDataRole.UserRole)
        self.phone_input.setItemData(2, False, Qt.ItemDataRole.UserRole)
        grid.addWidget(self.phone_input, 3, 1)

        # Фактична адреса
        grid.addWidget(QLabel("Фактична адреса:"), 4, 0)
        self.address_input = QComboBox()
        self.address_input.addItems(["Будь-яка", "З адресою", "Без адреси"])
        self.address_input.setItemData(0, "all", Qt.ItemDataRole.UserRole)
        self.address_input.setItemData(1, True, Qt.ItemDataRole.UserRole)
        self.address_input.setItemData(2, False, Qt.ItemDataRole.UserRole)
        grid.addWidget(self.address_input, 4, 1)

        main_layout.addLayout(grid)

        # Блок кнопок
        btn_layout = QHBoxLayout()
        self.apply_button = QPushButton("✅ Застосувати")
        self.clear_button = QPushButton("🔄 Очистити")
        self.cancel_button = QPushButton("✖️ Скасувати")

        # Стилізуємо головну кнопку
        self.apply_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        # Стилізуємо кнопку скасування (вже знайомий сірий стиль)
        self.cancel_button.setStyleSheet("background-color: #f0f3f5; color: #5d6d7e; border: 1px solid #d1d9e6;")

        btn_layout.addWidget(self.apply_button)
        btn_layout.addWidget(self.clear_button)
        btn_layout.addWidget(self.cancel_button)
        
        main_layout.addSpacing(10)
        main_layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # Зв'язки
        self.apply_button.clicked.connect(self.accept)
        self.clear_button.clicked.connect(self.clear_fields)
        self.cancel_button.clicked.connect(self.reject)
        
        self.load_current_filters()

    def get_filters(self):
        filters = {}

        if self.name_input.text():
            filters["name_filter"] = self.name_input.text()

        # Спрощена логіка перевірки
        inputs = {
            "type_filter": self.type_input,
            "email_required": self.email_input,
            "phone_required": self.phone_input,
            "address_required": self.address_input
        }

        for key, combo in inputs.items():
            data = combo.currentData(Qt.ItemDataRole.UserRole)
            if data != "all":
                filters[key] = data

        return filters

    def load_current_filters(self):
        if "name_filter" in self.current_filters:
            self.name_input.setText(self.current_filters["name_filter"])

        if "type_filter" in self.current_filters:
            type_value = self.current_filters["type_filter"]
            index = self.type_input.findData(type_value, Qt.ItemDataRole.UserRole)
            if index != -1:
                self.type_input.setCurrentIndex(index)

        if "email_required" in self.current_filters:
            email_value = self.current_filters["email_required"]
            index = self.email_input.findData(email_value, Qt.ItemDataRole.UserRole)
            if index != -1:
                self.email_input.setCurrentIndex(index)
        if "phone_required" in self.current_filters:
            phone_value = self.current_filters["phone_required"]
            index = self.phone_input.findData(phone_value, Qt.ItemDataRole.UserRole)
            if index != -1:
                self.phone_input.setCurrentIndex(index)
        if "address_required" in self.current_filters:  
            address_value = self.current_filters["address_required"]
            index = self.address_input.findData(address_value, Qt.ItemDataRole.UserRole)
            if index != -1:
                self.address_input.setCurrentIndex(index)

    def clear_fields(self):
        self.name_input.clear()
        self.type_input.setCurrentIndex(0)
        self.email_input.setCurrentIndex(0)
        self.phone_input.setCurrentIndex(0)
        self.address_input.setCurrentIndex(0)
