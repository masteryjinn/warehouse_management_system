from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QTableWidget, QTableWidgetItem, 
    QPushButton, QHBoxLayout, QMessageBox, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from services.api_client import ApiClient
from config.config import API_URL
from utils.load_styles import load_styles

class SupplierSelectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вибір постачальника")
        self.setMinimumSize(750, 550)
        self.selected_supplier = None
        self.api_url = API_URL + "/suppliers/select"
        
        # Застосування зовнішніх стилів
        self.setStyleSheet(load_styles())
        
        self.suppliers = []
        self.filtered_suppliers = []

        # --- Основний лейаут ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(12)

        # --- Заголовок ---
        title_label = QLabel("Виберіть постачальника")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)

        # --- Поле пошуку ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук за назвою або телефоном...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 1px solid #3498db;
                border-radius: 6px;
                font-size: 14px;
                color: #2c3e50;
                background-color: #f9faff;
            }
            QLineEdit:focus {
                border-color: #2980b9;
                background-color: #ffffff;
            }
        """)
        main_layout.addWidget(self.search_input)

        # --- Таблиця постачальників ---
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Назва компанії", "Телефон", "Email"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Перенесення слів та автоматична висота
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
            QTableWidget::item { padding: 6px; }
            QTableWidget::item:hover {
                background-color: #e8f3fc;
                color: #2c3e50;
            }
        """)
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        
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

        # Сигнали
        self.search_input.textChanged.connect(self.filter_suppliers)
        self.ok_button.clicked.connect(self.accept_selection)
        self.cancel_button.clicked.connect(self.reject)
        self.table.itemDoubleClicked.connect(self.accept_selection)

        self.load_suppliers()

    def load_suppliers(self):
        # Використовуємо ApiClient для консистентності
        response = ApiClient().get(self, self.api_url)
        if response and isinstance(response, dict) and "suppliers" in response:
            self.suppliers = response["suppliers"]
        else:
            # На випадок якщо API повертає прямий список
            self.suppliers = response if isinstance(response, list) else []
            
        self.filtered_suppliers = self.suppliers.copy()
        self.update_table()

    def update_table(self):
        self.table.setRowCount(0)
        for supplier in self.filtered_suppliers:
            row = self.table.rowCount()
            self.table.insertRow(row)
            # Назва постачальника, телефон та пошта
            self.table.setItem(row, 0, QTableWidgetItem(str(supplier.get("name", "Не вказано"))))
            self.table.setItem(row, 1, QTableWidgetItem(str(supplier.get("phone", "-"))))
            self.table.setItem(row, 2, QTableWidgetItem(str(supplier.get("email", "-"))))

        self.table.resizeRowsToContents()

    def filter_suppliers(self, text):
        search_text = text.lower()
        self.filtered_suppliers = [
            s for s in self.suppliers 
            if search_text in str(s.get("name", "")).lower() or 
               search_text in str(s.get("phone", "")).lower()
        ]
        self.update_table()

    def accept_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_supplier = self.filtered_suppliers[row]
            self.accept()
        else:
            QMessageBox.warning(self, "Вибір", "Будь ласка, виберіть постачальника.")

    def get_selected_supplier(self):
        return self.selected_supplier