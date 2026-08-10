from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QMessageBox, QLabel, QHeaderView)
from PyQt6.QtCore import Qt
import re
import pandas as pd

from windows.customers import CustomerDialog, FilterDialog
from managers.import_export_manager import ImportExportManager
from services.api_client import ApiClient

from utils import load_styles, fade_in_widget, show_scrollable_summary 
from config.config import API_URL

TYPE_MAP = {
    "business": "Юридична особа",
    "individual": "Фізична особа"
}

def translate_type_to_uk(type_en):
    return TYPE_MAP.get(type_en, type_en)

def translate_type_to_en(type_uk):
    inv_map = {v: k for k, v in TYPE_MAP.items()}
    return inv_map.get(type_uk, type_uk)


class CustomersTab(QWidget):
    def __init__(self):
        super().__init__() 
        self.current_page = 1
        self.items_per_page = 16
        self.total_pages = 1
        self.api_url = f"{API_URL}/customers"
        self.name_filter = None
        self.type_filter = None
        self.email_required = None
        self.phone_required = None
        self.address_required = None
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_customers()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по клієнту...")
        self.btn_search = QPushButton("🔍 Пошук")
        self.btn_clear = QPushButton("🔄 Скинути")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_clear)

        self.btn_search.clicked.connect(self.perform_search)
        self.btn_clear.clicked.connect(self.clear_search)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            'ID', 
            'Найменування / ПІБ', 
            'Категорія',          
            'E-mail', 
            'Контактний телефон', 
            'Адреса доставки'
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Додати")
        self.edit_btn = QPushButton("✏️ Редагувати")
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.filter_btn = QPushButton("📂 Фільтр")
        self.import_btn = QPushButton("📥 Імпорт")

        self.add_btn.clicked.connect(self.add_customer)
        self.edit_btn.clicked.connect(self.edit_customer)
        self.delete_btn.clicked.connect(self.delete_customer)
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        self.import_btn.clicked.connect(self.import_customers)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.filter_btn)
        button_layout.addWidget(self.import_btn)
        layout.addLayout(button_layout)

        # Кнопки для пагінації
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️ Попередня")
        self.next_btn = QPushButton("Наступна ➡️")
        self.page_label = QLabel(f"Сторінка {self.current_page} з {self.total_pages}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn.clicked.connect(self.on_prev_page)
        self.next_btn.clicked.connect(self.on_next_page)

        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)

        layout.addLayout(pagination_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

    def perform_search(self):
        self.current_page = 1
        self.load_customers()

    def clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.load_customers()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_customers()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_customers()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        
        # Оновлення інтерфейсу пагінації
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")

        # Логіка кнопок "Попередня" та "Наступна"
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def open_filter_dialog(self):
        # Створення діалогу без передачі фільтрів
        dialog = FilterDialog(self)  # Передаємо головне вікно
        if dialog.exec():
            self.apply_filters(dialog)
            self.current_page = 1
            self.load_customers()

    def apply_filters(self, dialog):
        filters = dialog.get_filters()
        self.name_filter = filters.get("name_filter")
        self.type_filter = filters.get("type_filter")
        self.email_required = filters.get("email_required")
        self.phone_required = filters.get("phone_required")
        self.address_required = filters.get("address_required")

    def fill_table_data(self, customers):
        self.table.setRowCount(len(customers))
        for row, customer in enumerate(customers):
            index_number = (self.current_page - 1) * self.items_per_page + row + 1
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(index_number)))
            self.table.setItem(row, 0, QTableWidgetItem(str(customer["customer_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(customer["name"]))
            translated_type = translate_type_to_uk(customer["type"])
            self.table.setItem(row, 2, QTableWidgetItem(translated_type))
            self.table.setItem(row, 3, QTableWidgetItem(customer.get("email", "")))
            self.table.setItem(row, 4, QTableWidgetItem(customer.get("phone", "")))
            self.table.setItem(row, 5, QTableWidgetItem(customer.get("address", "")))

        self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)


    def load_customers(self):    
        filters = {
            "name_filter": self.name_filter,
            "type_filter": self.type_filter,
            "email_required": self.email_required,
            "phone_required": self.phone_required,
            "address_required": self.address_required,
        }

        params = {
            "page": self.current_page,
            "limit": self.items_per_page,
            "search": self.search_input.text(),
        }

        if filters:
            params.update(filters)  # Додаємо фільтри до параметрі

        result = ApiClient.get(self, self.api_url, params=params)
        if result:
            customers = result.get("data", [])
            total_pages = result.get("total_pages", 1)
            current_page = result.get("current_page", 1)
            self.fill_table_data(customers)
            self.update_pagination(total_pages, current_page)
            fade_in_widget(self.table)

    def import_customers(self):
        # Розширений мапінг для підтримки різних назв колонок
        FIELD_MAP = {
            # Ім'я / Назва
            "Найменування / ПІБ": "name", "ПІБ": "name", "Назва": "name", 
            "Клієнт": "name", "Name": "name", "Customer": "name",
            # Тип
            "Тип": "type", "Категорія": "type", "Type": "type",
            # Адреса
            "Адреса": "address", "Місто": "address", "Address": "address", "Адреса доставки": "address", 
            "Юридична адреса": "address", "Фактична адреса": "address", "Location": "address",
            # Телефон
            "Телефон": "phone", "Мобільний": "phone", "Номер": "phone", "Phone": "phone", "Контактний телефон": "phone",
            # Email
            "Email": "email", "E-mail": "email", "Пошта": "email", "Mail": "email", "Електронна пошта": "email"
        }

        REVERSE_TYPE_MAP = {v: k for k, v in TYPE_MAP.items()}

        manager = ImportExportManager(parent=self)
        df = manager.import_data()
        if df is None:
            return

        # Перевірка, чи є у файлі хоча б одна колонка, що відповідає "name"
        actual_columns = df.columns.tolist()
        if not any(FIELD_MAP.get(col) == "name" for col in actual_columns):
            QMessageBox.warning(self, "Помилка структури", 
                                "У файлі не знайдено колонку з ім'ям клієнта (наприклад, 'Назва' або 'ПІБ').")
            return

        data = []
        for _, row in df.iterrows():
            new_item = {"contacts": {}}

            for ukr_field, value in row.items():
                eng_field = FIELD_MAP.get(ukr_field)
                if not eng_field or pd.isna(value):
                    continue

                value = str(value).strip()
                if not value:
                    continue

                # 1. Обробка ТИПУ
                if eng_field == "type":
                    if value in REVERSE_TYPE_MAP:
                        new_item[eng_field] = REVERSE_TYPE_MAP[value]
                    continue

                # 2. Обробка КОНТАКТІВ
                elif eng_field in ["phone", "email", "address"]:
                    if eng_field == "phone":
                        # Очищення від зайвих символів (дужки, пробіли, тире)
                        value = re.sub(r'[ ()\-]', '', value)
                        
                        if not value.startswith("+"):
                            if value.startswith("380"):
                                value = "+" + value
                            elif len(value) == 10 and value.startswith("0"):
                                value = "+38" + value
                        
                        if len(re.sub(r'\D', '', value)) < 10:
                            continue

                    elif eng_field == "email":
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if not re.match(email_pattern, value):
                            continue 

                    new_item["contacts"][eng_field] = value

                # 3. ВСІ ІНШІ ПОЛЯ (name)
                else:
                    new_item[eng_field] = value

            if "name" in new_item:
                data.append(new_item)

        if not data:
            QMessageBox.warning(self, "Помилка імпорту", "Не знайдено жодного коректного запису для імпорту.")
            return

        # Відправка на сервер
        result = ApiClient.post(
            self,
            f"{self.api_url}/import",
            data={"customers": data}
        )

        if result:
            message = result.get("message", "Імпорт клієнтів завершено успішно.")
            added = result.get("imported_names", [])
            duplicates = result.get("skipped_names", [])

            summary_text = f"{message}\n\n"
            if added:
                summary_text += "✅ Додані клієнти:\n" + "\n".join(f"• {name}" for name in added) + "\n\n"
            if duplicates:
                summary_text += "⚠️ Вже існували (пропущено):\n" + "\n".join(f"• {name}" for name in duplicates)

            show_scrollable_summary(self, "Результати імпорту клієнтів", summary_text)
            self.load_customers()

    def add_customer(self):
        dialog = CustomerDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, self.api_url, data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Клієнта додано")
                self.load_customers()


    def edit_customer(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть клієнта для редагування")
            return

        customer_id = int(self.table.item(current_row, 0).text())
        customer_data = {
            "name": self.table.item(current_row, 1).text(),
            "type": translate_type_to_en(self.table.item(current_row, 2).text()),
            "email": self.table.item(current_row, 3).text(),
            "phone": self.table.item(current_row, 4).text(),
            "address": self.table.item(current_row, 5).text(),
        }

        dialog = CustomerDialog(customer_data)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.put(self, f"{self.api_url}/{customer_id}", data=updated_data)
            if result:
                QMessageBox.information(self, "Успіх", "Клієнта оновлено")
                self.load_customers()


    def delete_customer(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть клієнта для видалення")
            return

        customer_id = int(self.table.item(current_row, 0).text())
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText("Ви впевнені, що хочете видалити клієнта?")
        confirm_box.setIcon(QMessageBox.Icon.Warning)
        confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
        confirm_box.button(QMessageBox.StandardButton.Yes).setText("Так")
        confirm_box.button(QMessageBox.StandardButton.No).setText("Ні")

        # Додатковий стиль (необов’язково)
        confirm_box.setStyleSheet("""
            QMessageBox {
                color: #ecf0f1;
                font-size: 14px;
            }
            QPushButton {
                min-width: 80px;
                font-size: 13px;
                padding: 5px 10px;
            }
        """)

        # Показ і перевірка відповіді
        confirm = confirm_box.exec()
        if confirm != QMessageBox.StandardButton.Yes:
            return

        result = ApiClient.delete(self, f"{self.api_url}/{customer_id}")
        if result:
            QMessageBox.information(self, "Успіх", "Клієнта видалено")
            if self.current_page > 1 and self.table.rowCount() == 1:
                self.current_page -= 1
            self.load_customers()