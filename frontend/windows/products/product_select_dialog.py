from PyQt6.QtWidgets import (
    QDialog, QHeaderView, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QHBoxLayout, QLabel
)
from PyQt6.QtCore import Qt
from services.api_client import ApiClient
from config.config import API_URL
from utils.load_styles import load_styles


class ProductSelectDialog(QDialog):
    def __init__(self,available_only=True):
        super().__init__()

        self.setWindowTitle("Вибір продукту")
        self.setMinimumSize(700, 450)
        self.selected_product = None
        self.api_url = API_URL + "/products/all-or-available"
        self.available_only = available_only

        self.setStyleSheet(load_styles())

        # --- Основний лейаут ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # --- Заголовок ---
        title_label = QLabel("Виберіть продукт")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)

        # --- Поле пошуку ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук продукту...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3498db;
                border-radius: 6px;
                font-size: 14px;
                background-color: #f9faff;
            }
            QLineEdit:focus {
                border-color: #2980b9;
                background-color: #ffffff;
            }
        """)
        main_layout.addWidget(self.search_input)

        # --- Таблиця продуктів ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.verticalHeader().setVisible(False)
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, header.ResizeMode.Stretch)      # Назва — розтягується
        header.setSectionResizeMode(1, header.ResizeMode.ResizeToContents)  # Постачальник
        header.setSectionResizeMode(2, header.ResizeMode.ResizeToContents)  # Кількість
        self.table.setHorizontalHeaderLabels(["Назва", "Постачальник", "Кількість"])
        self.table.setWordWrap(True)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.ResizeToContents)        

        self.table.setStyleSheet("""
            QTableWidget {
                font-size: 14px;
                border: 1px solid #d0d7de;
                border-radius: 6px;
                background-color: white;
                gridline-color: #e1e4e8;
                selection-background-color: #3498db;
                selection-color: white;
                outline: none;
            }

            QHeaderView::section {
                background-color: #f0f4f8;
                padding: 6px;
                font-size: 14px;
                font-weight: 600;
                border: 1px solid #d0d7de;
                color: #2c3e50;
            }

            QTableWidget::item {
                padding: 4px;
            }

            QTableWidget::item:hover {
                background-color: #e8f3fc;
                color: #2c3e50;
            }
        """)

        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)

        main_layout.addWidget(self.table, 1)

        # --- Кнопки ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("OK")
        self.ok_button.setDefault(True)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #2980b9; }
            QPushButton:pressed { background-color: #1c5d99; }
        """)

        self.cancel_button = QPushButton("Скасувати")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0;
                color: #555555;
                padding: 8px 20px;
                border-radius: 6px;
                font-size: 14px;
            }
            QPushButton:hover { background-color: #d0d0d0; }
            QPushButton:pressed { background-color: #b0b0b0; }
        """)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # --- Сигнали ---
        self.search_input.textChanged.connect(self.filter_products)
        self.ok_button.clicked.connect(self.accept_selection)
        self.cancel_button.clicked.connect(self.reject)
        self.table.doubleClicked.connect(self.accept_selection)

        # --- Завантаження ---
        self.load_products()

    # --------------------------------------------------
    # Завантаження продуктів
    # --------------------------------------------------
    def load_products(self):
        response = ApiClient().get(self, self.api_url, params={"available_only": self.available_only})
        if response and isinstance(response, dict) and "products" in response:
            self.products = response["products"]
        else:
            self.products = []
        self.filtered_products = self.products.copy()
        self.update_table()

    # --------------------------------------------------
    # Оновлення таблиці
    # --------------------------------------------------
    def update_table(self):
        self.table.setRowCount(len(self.filtered_products))

        for row, p in enumerate(self.filtered_products):
            self.table.setItem(row, 0, QTableWidgetItem(p["name"]))
            self.table.setItem(row, 1, QTableWidgetItem(p.get("supplier_name", "-")))
            self.table.setItem(row, 2, QTableWidgetItem(str(p.get("available_quantity", "-"))))
        
        self.table.resizeRowsToContents()

    # --------------------------------------------------
    # Фільтрація
    # --------------------------------------------------
    def filter_products(self, text):
        text = text.lower()
        self.filtered_products = [
            p for p in self.products if text in p["name"].lower()
        ]
        self.update_table()

    # --------------------------------------------------
    # Вибір продукту
    # --------------------------------------------------
    def accept_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            product = self.filtered_products[row]
            self.selected_product = product
            self.accept()

    def get_selected_product(self):
        return self.selected_product
