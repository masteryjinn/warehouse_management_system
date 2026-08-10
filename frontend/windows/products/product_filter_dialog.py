from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox
)
from PyQt6.QtCore import Qt
from services.api_client import ApiClient
from config.config import API_URL
from utils.load_styles import load_dialog_styles

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton,
    QHBoxLayout, QListWidget, QListWidgetItem, QFrame
)

class FilterDialog(QDialog):
    def __init__(self, parent=None, api_url=None, current_filters=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Фільтри")
        self.setFixedSize(380, 650) # Трохи ширше, але нижче
        self.api_url = api_url or API_URL
        self.current_filters = current_filters or {}
        self.sort_options = {
            "Без сортування": "",
            "Ціна: від дешевих ↑": "price_asc",
            "Ціна: від дорогих ↓": "price_desc",
            "Кількість: мало ↑": "quantity_asc",
            "Кількість: багато ↓": "quantity_desc",
            "Назва: А-Я": "name_asc",
            "Назва: Я-А": "name_desc",
            "Термін: найближчий ↑": "expiration_date_asc",
            "Термін: пізній ↓": "expiration_date_desc"
        }
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_dialog_styles())
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # 1. Пошук за назвою
        name_group = QVBoxLayout()
        name_group.setSpacing(5)
        name_label = QLabel("Назва продукту:")
        name_label.setStyleSheet("font-weight: bold;")
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Введіть частину назви...")
        name_group.addWidget(name_label)
        name_group.addWidget(self.name_input)
        main_layout.addLayout(name_group)

        # 2. Діапазон ціни (в один рядок)
        price_group = QVBoxLayout()
        price_group.setSpacing(5)
        price_title = QLabel("Діапазон ціни:")
        price_title.setStyleSheet("font-weight: bold;")
        
        price_inputs_layout = QHBoxLayout()
        self.min_price_input = QLineEdit()
        self.min_price_input.setPlaceholderText("Мін.")
        self.max_price_input = QLineEdit()
        self.max_price_input.setPlaceholderText("Макс.")
        
        price_inputs_layout.addWidget(self.min_price_input)
        price_inputs_layout.addWidget(QLabel("—"))
        price_inputs_layout.addWidget(self.max_price_input)
        
        price_group.addWidget(price_title)
        price_group.addLayout(price_inputs_layout)
        main_layout.addLayout(price_group)

        # 3. Сортування
        sort_group = QVBoxLayout()
        sort_group.setSpacing(5)
        sort_label = QLabel("Сортувати за:")
        sort_label.setStyleSheet("font-weight: bold;")
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(self.sort_options.keys())
        sort_group.addWidget(sort_label)
        sort_group.addWidget(self.sort_combo)
        main_layout.addLayout(sort_group)

        # 4. Категорії (з рамкою)
        cat_group = QVBoxLayout()
        cat_group.setSpacing(5)
        cat_label = QLabel("Категорії (виберіть кілька):")
        cat_label.setStyleSheet("font-weight: bold;")
        
        self.categories_list = QListWidget()
        self.categories_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.categories_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                background: white;
            }
            QListWidget::item { padding: 5px; }
            QListWidget::item:selected { background-color: #3498db; color: white; }
        """)
        
        cat_group.addWidget(cat_label)
        cat_group.addWidget(self.categories_list)
        main_layout.addWidget(cat_label)
        main_layout.addWidget(self.categories_list)

        # 5. Кнопки дій
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("✨ Застосувати")
        self.apply_button.setMinimumHeight(40)
        self.apply_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        
        self.clear_button = QPushButton("🔄 Очистити")
        self.clear_button.setMinimumHeight(40)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.clear_button)
        
        main_layout.addLayout(button_layout)
        
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.cancel_button.setMinimumHeight(40)
        self.cancel_button.setObjectName("cancel_button")
        main_layout.addWidget(self.cancel_button)

        # Зв'язки
        self.apply_button.clicked.connect(self.accept_with_validation)
        self.clear_button.clicked.connect(self.clear_fields)
        self.cancel_button.clicked.connect(self.reject)

        self.load_categories()
        if self.current_filters:
            self.load_current_filters()

    def load_categories(self):
        response = ApiClient().get(self, f"{self.api_url}/categories")
        if response and "categories" in response:
            self.categories = response["categories"]
            self.update_category_list()

    def update_category_list(self):
        self.categories_list.clear()
        for category in self.categories:
            item = QListWidgetItem(category)
            self.categories_list.addItem(item)
        self.load_current_filters()  # Переносимо, щоб не втрачати виділення після завантаження

    def get_filters(self):
        filters = {}
        if self.name_input.text().strip():
            filters["name"] = self.name_input.text().strip()
        if self.min_price_input.text().strip():
            filters["min_price"] = self.min_price_input.text().strip()
        if self.max_price_input.text().strip():
            filters["max_price"] = self.max_price_input.text().strip()

        sort_ukr = self.sort_combo.currentText()
        if sort_ukr:
            filters["sort"] = self.sort_options.get(sort_ukr, "")

        selected_categories = [item.text() for item in self.categories_list.selectedItems()]
        if selected_categories:
            filters["categories"] = selected_categories
        return filters

    def load_current_filters(self):
        self.name_input.setText(self.current_filters.get("name", ""))
        self.min_price_input.setText(self.current_filters.get("min_price", ""))
        self.max_price_input.setText(self.current_filters.get("max_price", ""))

        sort_value = self.current_filters.get("sort", "")
        ukr_label = next((k for k, v in self.sort_options.items() if v == sort_value), "")
        index = self.sort_combo.findText(ukr_label)
        self.sort_combo.setCurrentIndex(index if index != -1 else 0)

        selected_categories = self.current_filters.get("categories", [])
        for i in range(self.categories_list.count()):
            item = self.categories_list.item(i)
            item.setSelected(item.text() in selected_categories)

    def accept_with_validation(self):
        # Валідація діапазону цін
        min_price = self.min_price_input.text().strip()
        max_price = self.max_price_input.text().strip()
        if min_price and not min_price.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Помилка", "Мінімальна ціна повинна бути числом.")
            return
        if max_price and not max_price.replace('.', '', 1).isdigit():
            QMessageBox.warning(self, "Помилка", "Максимальна ціна повинна бути числом.")
            return
        if min_price and max_price and float(min_price) > float(max_price):
            QMessageBox.warning(self, "Помилка", "Мінімальна ціна не може бути більшою за максимальну.")
            return
        self.accept()

    def clear_fields(self):
        self.name_input.clear()
        self.min_price_input.clear()
        self.max_price_input.clear()
        self.sort_combo.setCurrentIndex(0)
        self.categories_list.clearSelection()
        self.current_filters = {}
