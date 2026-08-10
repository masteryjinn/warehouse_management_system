from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QMessageBox, QLabel, QCheckBox, QHeaderView)
from PyQt6.QtCore import Qt

from windows.warehouse.warehouse_dialog import WarehouseDialog
from services.api_client import ApiClient
from user_session.current_user import CurrentUser

from utils import load_styles, fade_in_widget
from config.config import API_URL

SECTION_TYPE_TRANSLATIONS = {
    "storage": "зберігання",
    "packaging": "пакування"
}


class SectionsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = CurrentUser().get_role()
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1
        self.api_url = f"{API_URL}/sections"
        self.search_query = ""
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_sections()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        layout = QVBoxLayout()

        # Пошук
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по секції...")
        self.btn_search = QPushButton("🔍 Пошук")
        self.btn_clear = QPushButton("♻️ Скинути")
        self.checkbox_empty_section = QCheckBox("Пустий склад")
        self.checkbox_empty_section.stateChanged.connect(self.perform_search)

        search_layout.addWidget(self.checkbox_empty_section)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_clear)

        self.btn_search.clicked.connect(self.perform_search)
        self.btn_clear.clicked.connect(self.clear_search)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(['ID', 'Секція', 'Тип зберігання', 'Розташування', 'Відповідальний', 'Контакт'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Додати")
        self.edit_btn = QPushButton("✏️ Змінити")
        self.delete_btn = QPushButton("🗑️ Видалити")

        self.add_btn.clicked.connect(self.add_section)
        self.edit_btn.clicked.connect(self.edit_section)
        self.delete_btn.clicked.connect(self.delete_section)
        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.edit_btn)
        button_layout.addWidget(self.delete_btn)
        layout.addLayout(button_layout)
        
        if self.user_role == "employee":
            self.add_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

        # Пагінація
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
        self.search_query = self.search_input.text()
        self.load_sections()

    def clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.search_query = ""
        self.load_sections()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_sections()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_sections()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def fill_table_data(self, sections):
        self.table.setRowCount(len(sections))
        
        for row, section in enumerate(sections):
            index_number = (self.current_page - 1) * self.items_per_page + row + 1
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(index_number)))
            self.table.setItem(row, 0, QTableWidgetItem(str(section["section_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(section["name"]))
            section_type_ukr = SECTION_TYPE_TRANSLATIONS.get(section["section_type"], section["section_type"])
            self.table.setItem(row, 2, QTableWidgetItem(section_type_ukr))
            self.table.setItem(row, 3, QTableWidgetItem(section["location"]))
            self.table.setItem(row, 4, QTableWidgetItem(section["employee_name"]))
            self.table.setItem(row, 5, QTableWidgetItem(section["employee_phone"]))
        
        self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def load_sections(self):
        params = {
            "page": self.current_page,
            "limit": self.items_per_page,
            "search": self.search_query,
            "is_empty": self.checkbox_empty_section.isChecked()
        }

        result = ApiClient.get(self, self.api_url, params=params)
        if result: 
            sections = result.get("data", [])
            total_pages = result.get("total_pages", 1)
            self.update_pagination(total_pages, self.current_page)
            self.fill_table_data(sections)
            fade_in_widget(self.table)

    def add_section(self):
        dialog = WarehouseDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, self.api_url, data=data)
            if result:
                self.show_message("Секцію успішно додано.")
                self.load_sections()

    def edit_section(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть секцію для редагування")
            return

        section_id = int(self.table.item(current_row, 0).text())
        section_data = {
            "name": self.table.item(current_row, 1).text(),
            "location": self.table.item(current_row, 3).text(),
            "employee_name": self.table.item(current_row, 4).text(),
        }

        dialog = WarehouseDialog(section_data)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.put(self, f"{self.api_url}/{section_id}", data=updated_data)
            if result:
                self.show_message("Секцію успішно оновлено.")
                self.load_sections()

    def delete_section(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть секцію для видалення")
            return

        section_id = int(self.table.item(current_row, 0).text())
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText("Ви впевнені, що хочете видалити секцію?")
        confirm_box.setIcon(QMessageBox.Icon.Warning)
        confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
        confirm_box.button(QMessageBox.StandardButton.Yes).setText("Так")
        confirm_box.button(QMessageBox.StandardButton.No).setText("Ні")

        # Показ і перевірка відповіді
        confirm = confirm_box.exec()
        if confirm != QMessageBox.StandardButton.Yes:
            return

        result = ApiClient.delete(self, f"{self.api_url}/{section_id}")
        if result:
            self.show_message("Секцію успішно видалено.")
            self.load_sections()

    def show_message(self, message):
        QMessageBox.information(self, "Інформація", message)

    def show_error(self, message):
        QMessageBox.critical(self, "Помилка", message)