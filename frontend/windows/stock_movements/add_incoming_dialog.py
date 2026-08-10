from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from windows.products.product_select_dialog import ProductSelectDialog
from utils.load_styles import load_styles


class AddIncomingDialog(QDialog):
    def __init__(self, order_id=-1):
        super().__init__()
        self.setWindowTitle("📥 Записати надходження товару")
        self.setMinimumSize(800, 450)
        self.order_id = order_id
        self.selected_products = []
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        main_layout = QVBoxLayout()

        title_label = QLabel("📥 Додати надходження товарів")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)

        top_buttons = QHBoxLayout()
        self.add_button = QPushButton("➕ Додати продукт")
        self.remove_button = QPushButton("🗑️ Видалити рядок")
        top_buttons.addWidget(self.add_button)
        top_buttons.addStretch()
        top_buttons.addWidget(self.remove_button)
        main_layout.addLayout(top_buttons)

        self.table = QTableWidget(0, 5) 
        self.table.setHorizontalHeaderLabels([
            "Назва", "Кількість", "Розмірність", "Секція", "Ціна закупівлі"  
        ])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setStyleSheet("""
            QTableWidget {
                background-color: #ffffff;
                font-size: 14px;
            }
            QHeaderView::section {
                background-color: #f2f2f2;
                font-weight: bold;
                padding: 6px;
                border: 1px solid #dddddd;
            }
        """)
        main_layout.addWidget(self.table)

        bottom_buttons = QHBoxLayout()
        self.confirm_button = QPushButton("✅ Підтвердити")
        self.cancel_button = QPushButton("✖️ Скасувати")
        bottom_buttons.addStretch()
        bottom_buttons.addWidget(self.confirm_button)
        bottom_buttons.addWidget(self.cancel_button)
        self.cancel_button.setObjectName("cancel_button")
        main_layout.addLayout(bottom_buttons)

        self.setLayout(main_layout)

        self.add_button.clicked.connect(self.add_product_row)
        self.remove_button.clicked.connect(self.remove_selected_row)
        self.confirm_button.clicked.connect(self.confirm_income)
        self.cancel_button.clicked.connect(self.reject)

    def add_product_row(self):
        search_dialog = ProductSelectDialog(available_only=False)
        if search_dialog.exec():
            product = search_dialog.get_selected_product()
            if not product:
                return

            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(product["name"])
            name_item.setData(Qt.ItemDataRole.UserRole, product)
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            qty_input = QLineEdit()
            qty_input.setPlaceholderText("Кількість")
            qty_input.setValidator(QIntValidator(1, 1000000))
            qty_input.setStyleSheet(self._default_qty_style())
            self.table.setCellWidget(row, 1, qty_input)

            unit_item = QTableWidgetItem(product["unit"])
            unit_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 2, unit_item)

            section_item = QTableWidgetItem(product["section_name"])
            section_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 3, section_item)

            price_input = QLineEdit()
            price_input.setPlaceholderText("Ціна")
            price_input.setStyleSheet(self._default_qty_style())
            price_input.setValidator(QDoubleValidator(0.01, 1000000.0, 2))
            self.table.setCellWidget(row, 4, price_input) 

            self.table.setRowHeight(row, 45)

    def remove_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
        else:
            QMessageBox.warning(self, "Увага", "Оберіть рядок для видалення.")

    def confirm_income(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Помилка", "Додайте хоча б один продукт.")
            return

        all_valid = True
        first_invalid_input = None

        for row in range(self.table.rowCount()):
            qty_input = self.table.cellWidget(row, 1)
            if not qty_input:
                continue
            qty_text = qty_input.text()
            if not qty_text.isdigit() or int(qty_text) <= 0:
                qty_input.setStyleSheet(self._error_qty_style())
                if not first_invalid_input:
                    first_invalid_input = qty_input
                all_valid = False
            else:
                qty_input.setStyleSheet(self._default_qty_style())

            price_input = self.table.cellWidget(row, 4)
            if not price_input or not price_input.text().replace('.', '', 1).isdigit() or float(price_input.text()) <= 0:
                price_input.setStyleSheet(self._error_qty_style())
                if not first_invalid_input:
                    first_invalid_input = price_input
                all_valid = False
            else:
                price_input.setStyleSheet(self._default_qty_style())

        if not all_valid:
            QMessageBox.warning(self, "Помилка", "Будь ласка, перевірте всі кількості — вони мають бути додатніми числами.")
            if first_invalid_input:
                first_invalid_input.setFocus()
            return

        self.accept()

    def get_income_items(self):
        items = []
        for row in range(self.table.rowCount()):
            name_item = self.table.item(row, 0)
            if not name_item:
                continue
            product = name_item.data(Qt.ItemDataRole.UserRole)

            qty_input = self.table.cellWidget(row, 1)
            if not qty_input or not qty_input.text().isdigit():
                continue
            qty = int(qty_input.text())
            if qty <= 0:
                continue

            price_input = self.table.cellWidget(row, 4)
            if not price_input or not price_input.text().replace('.', '', 1).isdigit():
                continue
            price = float(price_input.text())
            if price <= 0:
                continue

            items.append({
                "product_id": product["product_id"],
                "quantity": qty,
                "unit": product["unit"],
                "section": product["section_name"],
                "purchase_price": price  
            })

        return items

    def _default_qty_style(self):
        return """
            QLineEdit {
                padding: 6px;
                font-size: 14px;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border-color: #3498db;
                background-color: #ffffff;
            }
        """

    def _error_qty_style(self):
        return """
            QLineEdit {
                padding: 6px;
                font-size: 14px;
                border: 1px solid red;
                border-radius: 4px;
                background-color: #ffe6e6;
            }
        """
