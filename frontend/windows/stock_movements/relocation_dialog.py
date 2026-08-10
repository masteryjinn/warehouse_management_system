from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from services.api_client import ApiClient
from windows.products.product_select_dialog import ProductSelectDialog
from utils.load_styles import load_styles, load_combobox_styles
from config.config import API_URL   


class RelocationDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📦 Переміщення між секціями")
        self.setMinimumSize(750, 500)
        self.setStyleSheet(load_styles())

        self.sections = []
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_sections()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Формування переміщення товарів")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        #підказка, що при 0 кількості запис не буде робитися, просто номінально видалиться і додаватиметься з новою секцією
        title.setToolTip("При 0 кількості запис не буде робитися, просто номінально видалиться і додаватиметься з новою секцією")
        main_layout.addWidget(title)


        # Секція вибору
        section_layout = QHBoxLayout()
        section_label = QLabel("🎯 Цільова секція (куди):")
        self.section_combo = QComboBox()
        self.section_combo.setStyleSheet(load_combobox_styles())
        section_layout.addWidget(section_label)
        section_layout.addWidget(self.section_combo)
        section_layout.addStretch()
        main_layout.addLayout(section_layout)

        # Верхній ряд кнопок
        top_buttons = QHBoxLayout()
        self.add_button = QPushButton("➕ Додати продукт")
        self.remove_button = QPushButton("🗑️ Видалити рядок")
        top_buttons.addWidget(self.add_button)
        top_buttons.addStretch()
        top_buttons.addWidget(self.remove_button)
        main_layout.addLayout(top_buttons)

        # Таблиця
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Назва продукту", "Кількість", "Поточна секція"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        # Нижній ряд кнопок
        bottom_buttons = QHBoxLayout()
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.confirm_button = QPushButton("✅ Підтвердити переміщення")
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.confirm_button)
        bottom_buttons.addWidget(self.cancel_button)
        self.cancel_button.setObjectName("cancel_button")
        main_layout.addLayout(bottom_buttons)

        self.setLayout(main_layout)

        # Зв'язки
        self.add_button.clicked.connect(self.open_product_search)
        self.remove_button.clicked.connect(self.remove_selected_row)
        self.confirm_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

    def load_sections(self):
        response = ApiClient().get(self, API_URL + "/sections/full")
        if response and "data" in response:
            self.sections = response["data"]
            self.section_combo.clear()
            for section in self.sections:
                #print(f"Завантажена секція: {section['name']} (ID: {section['section_id']})") 
                self.section_combo.addItem(section["name"], section["section_id"])

            self.section_combo.setCurrentIndex(0)  # Встановлюємо перший елемент як вибраний за замовчуванням

    def open_product_search(self):
        dialog = ProductSelectDialog(available_only=False)
        if dialog.exec():
            product = dialog.get_selected_product()
            if product:
                # Уникнення повторів
                for row in range(self.table.rowCount()):
                    existing_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
                    if product["product_id"] == existing_id:
                        QMessageBox.warning(self, "Увага", "Цей товар вже додано.")
                        return

                row = self.table.rowCount()
                self.table.insertRow(row)

                # Назва
                name_item = QTableWidgetItem(product["name"])
                name_item.setData(Qt.ItemDataRole.UserRole, product["product_id"])
                name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 0, name_item)

                # Кількість — текстом
                qty_item = QTableWidgetItem(str(product["available_quantity"]))
                qty_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 1, qty_item)

                # Поточна секція
                section_item = QTableWidgetItem(product["section_name"])
                section_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 2, section_item)

    def remove_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
        else:
            QMessageBox.warning(self, "Увага", "Оберіть рядок для видалення.")

    def get_data(self):
        index = self.section_combo.currentIndex()
        if index < 0:
            QMessageBox.warning(self, "Помилка", "Оберіть секцію для переміщення.")
            return None

        section_id = self.section_combo.itemData(index)
        section_name = self.section_combo.currentText()
        items = []

        for row in range(self.table.rowCount()):
            product_id = self.table.item(row, 0).data(Qt.ItemDataRole.UserRole)
            quantity = int(self.table.item(row, 1).text())
            current_section = self.table.item(row, 2).text()

            items.append({
                "product_id": product_id,
                "quantity": quantity,
                "current_section": current_section
            })

        if not items:
            QMessageBox.warning(self, "Помилка", "Список товарів порожній.")
            return None

        return {
            "section_id": section_id,
            "items": items
        }

    def validate_and_accept(self):
        data = self.get_data()
        if not data:
            return

        target_name = self.section_combo.currentText()
        invalid = []

        for row in range(self.table.rowCount()):
            name = self.table.item(row, 0).text()
            current_section = self.table.item(row, 2).text()

            if current_section == target_name:
                invalid.append(name)

        if invalid:
            QMessageBox.warning(
                self,
                "Помилка переміщення",
                f"Наступні товари вже у секції '{target_name}':\n- " + "\n- ".join(invalid)
            )
            return


        self.accept()

    def get_final_data(self):
        return self.get_data()
