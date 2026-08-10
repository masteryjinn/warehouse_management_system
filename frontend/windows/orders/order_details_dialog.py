from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QSpinBox, QMessageBox, QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from windows.products.product_select_dialog import ProductSelectDialog
from utils.load_styles import load_styles

class OrderCreateDialog(QDialog):
    def __init__(self, order_id):
        super().__init__()
        self.setWindowTitle("🛒 Формування замовлення")
        self.setMinimumSize(800, 500)
        self.order_id = order_id
        self.selected_products = []  
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        main_layout = QVBoxLayout()

        self.order_label = QLabel(f"📦 Замовлення №{self.order_id}")
        main_layout.addWidget(self.order_label)

        # Верхній ряд кнопок
        top_button_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Додати продукт")
        self.remove_button = QPushButton("🗑️ Видалити рядок")
        top_button_layout.addWidget(self.add_button)
        top_button_layout.addStretch()
        top_button_layout.addWidget(self.remove_button)
        main_layout.addLayout(top_button_layout)

        # Таблиця
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Назва", "Кількість", "Од. вим.", "Ціна/шт.", "Сума", "Секція"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        main_layout.addWidget(self.table)

        # Сума
        self.total_label = QLabel("Разом до сплати: 0.00 грн")
        self.total_label.setStyleSheet("""
            font-size: 20px; 
            font-weight: bold; 
            color: #57a9b5; 
            background: #f0f0f0; 
            padding: 10px 20px; 
            border-radius: 5px;
        """)
        main_layout.addWidget(self.total_label)

        # Нижній ряд кнопок
        bottom_button_layout = QHBoxLayout()
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.cancel_button.setObjectName("cancel_button")
        self.confirm_button = QPushButton("✅ Підтвердити")
        bottom_button_layout.addStretch()
        bottom_button_layout.addWidget(self.confirm_button)
        bottom_button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(bottom_button_layout)

        self.setLayout(main_layout)

        # Сигнали
        self.add_button.clicked.connect(self.add_product_row)
        self.remove_button.clicked.connect(self.remove_selected_row)
        self.confirm_button.clicked.connect(self.confirm_order)
        self.cancel_button.clicked.connect(self.reject)

    def add_product_row(self):
        search_dialog = ProductSelectDialog(available_only=True)
        if search_dialog.exec():
            selected_product = search_dialog.get_selected_product()
            if not selected_product:
                return

            if any(p["product_id"] == selected_product["product_id"] for p in self.selected_products):
                QMessageBox.warning(self, "Помилка", "Цей продукт вже доданий до замовлення.")
                return

            row = self.table.rowCount()
            self.table.insertRow(row)

            name_item = QTableWidgetItem(selected_product["name"])
            name_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 0, name_item)

            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(selected_product["available_quantity"])
            qty_spin.setValue(1)
            qty_spin.valueChanged.connect(self.update_total_sum)
            self.table.setCellWidget(row, 1, qty_spin)

            dimension_item = QTableWidgetItem(selected_product["unit"])
            dimension_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 2, dimension_item)

            price_item = QTableWidgetItem(f"{selected_product['price']:.2f}")
            price_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 3, price_item)

            total_item = QTableWidgetItem(f"{selected_product['price']:.2f}")
            total_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 4, total_item)


            section_item = QTableWidgetItem(selected_product["section_name"])
            section_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 5, section_item)

            self.selected_products.append(selected_product)
            self.update_total_sum()

    def remove_selected_row(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            self.table.removeRow(current_row)
            if current_row < len(self.selected_products):
                del self.selected_products[current_row]
            self.update_total_sum()
            
    def update_total_sum(self):
        total = 0.0
        for row in range(self.table.rowCount()):
            product = self.selected_products[row]
            qty_widget = self.table.cellWidget(row, 1)
            qty = qty_widget.value() if qty_widget else 1
            row_sum = product["price"] * qty
            total += row_sum

            sum_item = self.table.item(row, 4)
            if sum_item:
                sum_item.setText(f"{row_sum:.2f}")
            else:
                sum_item = QTableWidgetItem(f"{row_sum:.2f}")
                sum_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.table.setItem(row, 4, sum_item)

        self.total_label.setText(f"Загальна сума: {total:.2f} грн")

    def confirm_order(self):
        if self.table.rowCount() == 0:
            QMessageBox.warning(self, "Помилка", "Додайте хоча б один продукт.")
            return
        self.accept()

    def get_order_items(self):
        items = []
        for row, product in enumerate(self.selected_products):
            qty_widget = self.table.cellWidget(row, 1)
            qty = qty_widget.value() if qty_widget else 1
            items.append({
                "product_id": product["product_id"],
                "quantity": qty,
                "unit": product["unit"],
                "price": product["price"],
                "section": product["section_name"]
            })
        return items