from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QMessageBox, QLabel, QHeaderView)
from PyQt6.QtCore import Qt
import re
import pandas as pd

from managers.import_export_manager import ImportExportManager
from windows.suppliers import SupplierDialog, FilterDialog
from services.api_client import ApiClient

from utils import load_styles, fade_in_widget, show_scrollable_summary
from config.config import API_URL

class SuppliersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        self.api_url = f"{API_URL}/suppliers"
        self.name_filter = None
        self.type_filter = None
        self.email_required = None
        self.phone_required = None
        self.address_required = None
        self.filters=None
        self.type_dict = {
            "Виробник": "manufacturer",
            "Дистриб'ютор": "distributor",
            "Оптовий продавець": "wholesaler"
        }
        self.reverse_type_dict = {v: k for k, v in self.type_dict.items()}
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        layout = QVBoxLayout()

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по постачальникам...")
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
            'Назва компанії',     
            'Вид діяльності',   
            'E-mail', 
            'Контактний телефон', 
            'Юридична адреса'
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

        self.add_btn.clicked.connect(self.add_supplier)
        self.edit_btn.clicked.connect(self.edit_supplier)
        self.delete_btn.clicked.connect(self.delete_supplier)
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        self.import_btn.clicked.connect(self.import_suppliers)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.filter_btn)
        button_layout.addWidget(self.import_btn)
        layout.addLayout(button_layout)

        # Кнопки для пагінації
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️ Попередня")
        self.next_btn = QPushButton("➡️ Наступна")
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
        self.load_suppliers()

    def clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.load_suppliers()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_suppliers()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_suppliers()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_suppliers()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def open_filter_dialog(self):
        dialog = FilterDialog(self)  # Передаємо головне вікно
        if dialog.exec():
            self.apply_filters(dialog)
            self.current_page=1
            self.load_suppliers()

    def apply_filters(self, dialog):
        self.filters = dialog.get_filters()
        self.name_filter = self.filters.get("name_filter")
        self.type_filter = self.filters.get("type_filter")
        self.email_required = self.filters.get("email_required")
        self.phone_required = self.filters.get("phone_required")
        self.address_required = self.filters.get("address_required")

    def fill_table(self, suppliers):
        self.table.setRowCount(len(suppliers))
        for row, supplier in enumerate(suppliers):
            index_number = (self.current_page - 1) * self.items_per_page + row + 1
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(index_number)))
            self.table.setItem(row, 0, QTableWidgetItem(str(supplier["supplier_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(supplier["name"]))
            
            # ТУТ — з англійської в українську
            type_ua = self.reverse_type_dict.get(supplier["type"], supplier["type"])
            self.table.setItem(row, 2, QTableWidgetItem(type_ua))

            self.table.setItem(row, 3, QTableWidgetItem(supplier.get("email", "")))
            self.table.setItem(row, 4, QTableWidgetItem(supplier.get("phone", "")))
            self.table.setItem(row, 5, QTableWidgetItem(supplier.get("address", "")))

        self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def load_suppliers(self):
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
        if not result:
            return
        suppliers = result.get("data", [])
        self.update_pagination(result.get("total_pages", 1), result.get("current_page", 1))
        self.fill_table(suppliers)
        fade_in_widget(self.table)



    def import_suppliers(self):
        FIELD_MAP = {
            # Назва компанії
            "Назва компанії": "name",
            "Назва": "name",
            "Компанія": "name",
            "Організація": "name",
            "Постачальник": "name",
            "Контрагент": "name",
            "Ім'я": "name",
            "Name": "name",
            "Company": "name",

            # Тип
            "Тип": "type",
            "Категорія": "type",
            "Група": "type",
            "Type": "type",
            "Category": "type",

            # Адреса
            "Адреса": "address",
            "Адреса реєстрації": "address",
            "Юридична адреса": "address",
            "Фактична адреса": "address",
            "Address": "address",

            # Телефон
            "Телефон": "phone",
            "Номер телефону": "phone",
            "Контактний телефон": "phone",
            "Мобільний": "phone",
            "Моб. телефон": "phone",
            "Phone": "phone",
            "Tel": "phone",

            # Email
            "Email": "email",
            "E-mail": "email",
            "Пошта": "email",
            "Електронна пошта": "email",
            "Ел. пошта": "email",
            "Mail": "email"
        }

        manager = ImportExportManager(parent=self)
        df = manager.import_data()
        if df is None:
            return
        actual_columns = [str(c).strip() for c in df.columns]
        has_name_column = any(FIELD_MAP.get(col) == "name" for col in actual_columns)

        if not has_name_column:
            QMessageBox.warning(self, "Помилка файлу", 
                                "У файлі не знайдено колонку з назвою постачальника (наприклад, 'Назва' або 'Компанія').")
            return
        data = []
        for _, row in df.iterrows():
            new_item = {"contacts": {}}
            
            for ukr_field, value in row.items():
                # Приклад при зчитуванні колонок:
                ukr_field_clean = str(ukr_field).strip().capitalize() # або .lower()
                eng_field = FIELD_MAP.get(ukr_field_clean)
                if not eng_field or pd.isna(value):
                    continue

                value = str(value).strip()
                if not value:
                    continue

                # 1. Валідація Типу постачальника
                if eng_field == "type":
                    if value in self.type_dict:
                        new_item["type"] = self.type_dict[value]
                    continue

                # 2. Валідація Контактів (телефон та email)
                elif eng_field in ["phone", "email", "address"]:
                    if eng_field == "phone":
                        # Очищення та форматування під +380
                        value = value.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
                        if not value.startswith("+"):
                            if value.startswith("380"):
                                value = "+" + value
                            elif len(value) == 10 and value.startswith("0"):
                                value = "+38" + value
                        
                        # Мінімальна валідація довжини
                        if len(re.sub(r'\D', '', value)) < 10:
                            continue

                    elif eng_field == "email":
                        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                        if not re.match(email_pattern, value):
                            continue

                    new_item["contacts"][eng_field] = value

                # 3. Назва компанії
                else:
                    new_item[eng_field] = value

            # Додаємо лише якщо є назва (обов'язкове поле)
            if "name" in new_item:
                data.append(new_item)

        if not data:
            QMessageBox.warning(self, "Помилка імпорту", "Немає коректних даних для імпорту. Переконайтеся, що в файлі є принаймні стовпець 'Назва компанії' з правильними даними, а також перевірте формат контактів.")
            return
        if len(data) < len(df):
            QMessageBox.warning(self, "Увага", f"Деякі рядки були пропущені через відсутність обов'язкових полів або некоректний формат. Успішно імпортовано {len(data)} з {len(df)} записів.")

        # Відправка на сервер
        result = ApiClient.post(self, f"{self.api_url}/import", data={"suppliers": data})
        
        if result:
            message = result.get("message", "Імпорт постачальників завершено успішно.")
            added = result.get("imported_names", [])
            duplicates = result.get("skipped_names", [])

            summary_text = f"{message}\n\n"
            if added:
                summary_text += "✅ Додані постачальники:\n" + "\n".join(f"• {name}" for name in added) + "\n\n"
            if duplicates:
                summary_text += "⚠️ Вже існували:\n" + "\n".join(f"• {name}" for name in duplicates)

            show_scrollable_summary(self, "Результати імпорту постачальників", summary_text)
            self.load_suppliers()


    def add_supplier(self):
        dialog = SupplierDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, self.api_url, data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Постачальника додано")
                self.load_suppliers()


    def edit_supplier(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть постачальника для редагування")
            return

        supplier_id = int(self.table.item(current_row, 0).text())

        # З української в англійську
        type_ua = self.table.item(current_row, 2).text()
        type_en = self.type_dict.get(type_ua, type_ua)

        supplier_data = {
            "name": self.table.item(current_row, 1).text(),
            "type": type_en,
            "email": self.table.item(current_row, 3).text(),
            "phone": self.table.item(current_row, 4).text(),
            "address": self.table.item(current_row, 5).text(),
        }


        dialog = SupplierDialog(supplier_data)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.put(self, f"{self.api_url}/{supplier_id}", data=updated_data)
            if result:
                QMessageBox.information(self, "Успіх", "Дані постачальника оновлено")
                self.load_suppliers()

    def delete_supplier(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть постачальника для видалення")
            return

        supplier_id = int(self.table.item(current_row, 0).text())
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText("Ви впевнені, що хочете видалити постачальника?")
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

        result = ApiClient.delete(self, f"{self.api_url}/{supplier_id}")
        if result:
            QMessageBox.information(self, "Успіх", "Постачальника видалено")
            if self.table.rowCount() == 1 and self.current_page > 1:
                self.current_page -= 1
            self.load_suppliers()