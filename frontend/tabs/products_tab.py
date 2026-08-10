from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QMessageBox, QLabel, QCheckBox, QDialog,
                                QScrollArea, QComboBox, QHeaderView)
from PyQt6.QtCore import Qt
import pandas as pd
from datetime import datetime

from windows.products import FilterDialog, ProductDialog
from managers.import_export_manager import ImportExportManager
from services.api_client import ApiClient
from user_session.current_user import CurrentUser  

from config.config import API_URL
from utils import fade_in_widget, format_date
from utils.load_styles import load_styles, load_combobox_styles

class ProductsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = CurrentUser().get_role()
        self.current_page = 1
        self.items_per_page = 14
        self.total_pages = 1
        self.api_url = API_URL + "/products"
        self.name_filter = None
        self.category_filter = None
        self.price_min = None
        self.price_max = None
        self.sort_order = None
        self.filters= None
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_products()
        self.load_sections()

    def init_ui(self):
        self.setStyleSheet(load_styles())
        
        layout = QVBoxLayout()

        # Створюємо основний лейаут для пошуку
        search_layout = QHBoxLayout()

        # Поле для введення тексту пошуку
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по продукту...")

        # Кнопки пошуку і скидання
        self.btn_search = QPushButton("🔍 Пошук")
        self.btn_clear = QPushButton("🔄 Скинути")

        # Чекбокси для фільтрації за терміном придатності
        self.checkbox_expire_date = QCheckBox("Мають термін придатності")
        self.checkbox_expire_date.stateChanged.connect(self.perform_search)
        self.checkbox_has_expire = QCheckBox("Термін придатності закінчився")
        self.checkbox_has_expire.stateChanged.connect(self.perform_search)
        # Створюємо комбобокс для вибору секції
        self.section_combobox = QComboBox()
        self.section_combobox.addItem("Усі секції")  # Значення за замовчуванням
        self.section_combobox.setStyleSheet(load_combobox_styles())
        self.section_combobox.currentTextChanged.connect(self.perform_search)

        # Організуємо чекбокси в горизонтальний лейаут
        checkbox_layout = QVBoxLayout()
        checkbox_layout.addWidget(self.checkbox_expire_date)
        checkbox_layout.addWidget(self.checkbox_has_expire)
        checkbox_layout.addWidget(self.section_combobox)


        # Додаємо всі елементи до основного лейауту
        search_layout.addLayout(checkbox_layout)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_clear)

        # З'єднуємо кнопки з відповідними методами
        self.btn_search.clicked.connect(self.perform_search)
        self.btn_clear.clicked.connect(self.clear_search)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'ID', 'Ім’я', 'Категорія', 'Ціна', 'Опис', 'Кількість',
            'Од. виміру', 'Термін\nпридатності', 'Постачальник', 'Секція', 'Опис(прихований)'  
        ])
        layout.addLayout(search_layout)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.cellClicked.connect(self.handle_table_click)
        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Додати")
        self.edit_btn = QPushButton("✏️ Редагувати")
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.filter_btn = QPushButton("🔍 Фільтр")
        self.export_btn = QPushButton("💾 Експорт")
        self.import_btn = QPushButton("📂 Імпорт")

        if self.user_role == "employee":
            self.add_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.import_btn.setEnabled(False)
            self.export_btn.setEnabled(False)

        self.export_btn.clicked.connect(self.export_products)
        self.add_btn.clicked.connect(self.add_product)
        self.edit_btn.clicked.connect(self.edit_product)
        self.delete_btn.clicked.connect(self.delete_product)
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        self.import_btn.clicked.connect(self.import_products)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.filter_btn)
        button_layout.addWidget(self.export_btn)
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

    def handle_table_click(self, row, column):
        if column == 4:  # якщо колонка з "деталі"
            item = self.table.item(row, 10)  # колонка з описом
            description = item.text() if item else ""
            self.show_description(description)

    def perform_search(self):
        self.current_page = 1
        self.load_products()

    def clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.load_products()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_products()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_products()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def open_filter_dialog(self):
        dialog = FilterDialog(self, self.api_url,self.filters)
        if dialog.exec():
            self.apply_filters(dialog)
            self.current_page = 1
            self.load_products()

    def apply_filters(self, dialog):
        self.filters = dialog.get_filters()
        self.name_filter = self.filters.get("name")
        self.category_filter = self.filters.get("categories")
        self.price_min = self.filters.get("min_price")
        self.price_max = self.filters.get("max_price")
        self.sort_order = self.filters.get("sort")  
        
    def show_description(self, description):
        dialog = QDialog(self)
        dialog.setWindowTitle("Опис продукту")
        dialog.resize(600, 400)  # Фіксований розмір із можливістю прокрутки

        layout = QVBoxLayout()

        # Створюємо QLabel з описом
        label = QLabel(description if description else "Опис відсутній")
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setStyleSheet("font-size: 16px; padding: 5px;")
        label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # Прокручувана область
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(label)

        layout.addWidget(scroll_area)

        # Кнопка закриття
        close_btn = QPushButton("Закрити")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn, alignment=Qt.AlignmentFlag.AlignRight)

        dialog.setLayout(layout)
        dialog.exec()

    def load_sections(self):
            result = ApiClient.get(self, f"{API_URL}/sections/full")
            if result:
                sections = result.get("data", [])
                self.section_combobox.clear()
                self.section_combobox.addItem("Усі секції")
                for section in sections:
                    name = section.get("name")
                    if name:
                        self.section_combobox.addItem(name)

    def fill_table(self, products):
        self.table.setRowCount(len(products))
        for row, product in enumerate(products):
            index_number = (self.current_page - 1) * self.items_per_page + row + 1
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(index_number)))
            self.table.setItem(row, 0, QTableWidgetItem(str(product["product_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(product["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(product["category_name"]))
            self.table.setItem(row, 3, QTableWidgetItem(str(product["price"])))
            desc_item = QTableWidgetItem("ℹ️")
            desc_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            desc_item.setForeground(Qt.GlobalColor.blue)
            desc_item.setToolTip("Натисніть для перегляду опису")
            self.table.setItem(row, 4, desc_item)
            #підсвічування кількості яка менше 5
            quantity_item = QTableWidgetItem(str(product["quantity"]))
            if product["quantity"] < 5:
                quantity_item.setBackground(Qt.GlobalColor.red)
                quantity_item.setForeground(Qt.GlobalColor.white)
            self.table.setItem(row, 5, quantity_item)
            self.table.setItem(row, 6, QTableWidgetItem(str(product["unit"])))
            self.table.setItem(row, 7, QTableWidgetItem(format_date(product.get("expiration_date"), show_time=False)))
            self.table.setItem(row, 8, QTableWidgetItem(product.get("supplier_name", "")))
            self.table.setItem(row, 9, QTableWidgetItem(product.get("section_name", "")))
            self.table.setItem(row, 10, QTableWidgetItem(product.get("description", "")))
        
        self.table.setColumnHidden(0, True)
        self.table.setColumnHidden(10, True) 
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def load_products(self):
        filters = {
            "name_filter": self.name_filter,
            "category_filter": self.category_filter,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "sort_order": self.sort_order,
        }

        params = {
            "page": self.current_page,
            "limit": self.items_per_page,
            "search": self.search_input.text(),
            "expire_date": self.checkbox_expire_date.isChecked(),
            "has_expired": self.checkbox_has_expire.isChecked()
        }

        if filters:
            for key, value in filters.items():
                if value is not None and value != "":
                    params[key] = value

        result = ApiClient.get(self, self.api_url, params=params)
        if result:
            products = result.get("data", [])
            total_pages = result.get("total_pages", 1)
            current_page = result.get("current_page", 1)
            self.update_pagination(total_pages, current_page)
            self.fill_table(products)
            fade_in_widget(self.table)

    def export_products(self):
        filters = {
            "name_filter": self.name_filter,
            "category_filter": self.category_filter,
            "price_min": self.price_min,
            "price_max": self.price_max,
            "sort_order": self.sort_order,
        }

        params = {
            "search": self.search_input.text(),
            "expire_date": self.checkbox_expire_date.isChecked(),
            "has_expired": self.checkbox_has_expire.isChecked()
        }

        if filters:
            for key, value in filters.items():
                if value is not None and value != "":
                    params[key] = value

        result = ApiClient.get(self, f"{self.api_url}/full", params=params)

        if result:
            products_data = result.get("products", [])

            # Маппінг англійських ключів у українські заголовки
            headers_map = {
                "product_id": "ID продукту",
                "name": "Назва",
                "description": "Опис",
                "price": "Ціна",
                "quantity": "Кількість",
                "expiration_date": "Термін придатності",
                "unit": "Одиниця",
                "category_name": "Категорія",
                "supplier_name": "Постачальник",
                "section_name": "Секція"
            }

            # Підготовка даних для експорту
            rows = []
            for item in products_data:
                row = [item[key] for key in headers_map.keys()]
                rows.append(row)
                # Заголовки українською
            headers = list(headers_map.values())
            # Виклик менеджера
            exporter = ImportExportManager(self)
            exporter.export_data(rows, headers)

    def import_products(self):
        # Відкриття файлу
        importer = ImportExportManager(self)
        df = importer.import_data()  # pandas DataFrame або None
        if df is None:
            return None
        
        # Обов'язкові колонки
        required_columns = [
            "Назва", "Опис", "Ціна", "Кількість",
            "Термін придатності", "Одиниця", "Категорія",
            "Постачальник", "Секція"
        ]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            QMessageBox.warning(self, "Помилка", f"У файлі відсутні колонки: {', '.join(missing_cols)}")
            return None
        
        headers_map = {
            "ID продукту": "product_id",
            "Назва": "name",
            "Опис": "description",
            "Ціна": "price",
            "Кількість": "quantity",
            "Термін придатності": "expiration_date",
            "Одиниця": "unit",
            "Категорія": "category_name",
            "Постачальник": "supplier_name",
            "Секція": "section_name"
        }

        products_to_upload = []
        errors = []

        for idx, row in df.iterrows():
            item = {}
            row_errors = []
            for col, key in headers_map.items():
                if col == "ID продукту" and (col not in df.columns or pd.isna(row[col]) or row[col] == ""):
                    continue

                value = row[col]

                if pd.isna(value):
                    value = None

                    # Числа
                if key in ("price", "quantity") and value is not None:
                    try:
                        value = float(str(value).replace(",", ".")) if key == "price" else int(value)
                    except (ValueError, TypeError):
                        row_errors.append(f"{key}: некоректне значення '{value}'")
                        value = None

                # Дата
                if key == "expiration_date" and value is not None:
                    for fmt in ("%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y"):
                        try:
                            value = datetime.strptime(str(value), fmt).date()
                            # Перетворюємо у рядок перед відправкою на сервер
                            value = value.isoformat()  # 'YYYY-MM-DD'
                            break
                        except ValueError:
                            continue
                    else:
                        row_errors.append(f"{key}: некоректна дата '{value}'")
                        value = None

                item[key] = value

            if row_errors:
                errors.append({"row": idx + 2, "errors": row_errors})  # +2 щоб відобразити Excel рядок
            
            products_to_upload.append(item)

        result = ApiClient.post(self, f"{self.api_url}/import", data={"products": products_to_upload})
        if result:
            msg = "Дані успішно імпортовано на сервер!"
            if errors:
                msg += "\n\nПримітка: деякі рядки мали некоректні значення:\n"
                for err in errors:
                    msg += f"Рядок {err['row']}: {', '.join(err['errors'])}\n"
            QMessageBox.information(self, "Успіх", msg)
            self.load_products()

    def add_product(self):
        dialog = ProductDialog(None, self.api_url)
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, self.api_url, data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Продукт успішно додано")
                self.load_products()

    def edit_product(self):
        selected_row = self.table.selectedIndexes()
        if not selected_row:
            QMessageBox.warning(self, "Увага", "Будь ласка, виберіть продукт для редагування.")
            return

        product_id = self.table.item(selected_row[0].row(), 0).text()
        product_data = {
            "name": self.table.item(selected_row[0].row(), 1).text(),
            "category": self.table.item(selected_row[0].row(), 2).text(),
            "price": self.table.item(selected_row[0].row(), 3).text(),
            "description": self.table.item(selected_row[0].row(), 10).text(),
            "quantity": self.table.item(selected_row[0].row(), 5).text(),
            "unit": self.table.item(selected_row[0].row(), 6).text(),
            "expiration_date": self.table.item(selected_row[0].row(), 7).text(),
            "supplier_name": self.table.item(selected_row[0].row(), 8).text()
        }

        dialog = ProductDialog(product_data, self.api_url)
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return

            result = ApiClient.put(self, f"{self.api_url}/{product_id}", data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Продукт успішно оновлено")
                self.load_products()

    def delete_product(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть продукт для видалення")
            return

        product_id = int(self.table.item(current_row, 0).text())
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText("Ви впевнені, що хочете видалити цей продукт?")
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

        result = ApiClient.delete(self, f"{self.api_url}/{product_id}")
        if result:
            QMessageBox.information(self, "Успіх", "Продукт успішно видалено")
            if self.table.rowCount() == 1 and self.current_page > 1:
                self.current_page -= 1
            self.load_products()