from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt
from services.api_client import ApiClient
from config.config import API_URL
from utils.load_styles import load_styles

class EmployeeSelectDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вибір працівника")
        self.setMinimumSize(850, 550) # Робимо широким для таблиці
        self.selected_employee = None
        self.api_url = f"{API_URL}/employees/select"
        
        self.setStyleSheet(load_styles())
        
        self.employees = []
        self.filtered_employees = []

        # --- Основний лейаут ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # --- Заголовок ---
        title_label = QLabel("Оберіть працівника зі списку")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1b263b;")
        main_layout.addWidget(title_label)

        # --- Пошук ---
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Пошук за ПІБ, посадою або телефоном...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #3498db;
                border-radius: 8px;
                font-size: 14px;
                background-color: #f9faff;
            }
            QLineEdit:focus { border-color: #3498db; background-color: white; }
        """)
        main_layout.addWidget(self.search_input)

        # --- Таблиця (QTableWidget) ---
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ПІБ працівника", "Посада", "Телефон", "Email"])
        self.table.verticalHeader().setVisible(False)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        
        # Стилізація таблиці
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d7de;
                border-radius: 8px;
                gridline-color: #f0f0f0;
                font-size: 14px;
                outline: none;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 10px;
                font-weight: bold;
                border: 1px solid #d0d7de;
                color: #2c3e50;
            }
            QTableWidget::item { padding: 10px; }
            QTableWidget::item:selected { background-color: #3498db; color: white; }
        """)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) # ПІБ розтягується
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)

        main_layout.addWidget(self.table, 1)

        # --- Кнопки ---
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self.ok_button = QPushButton("✅ Підтвердити вибір")
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 10px 25px;
                border-radius: 6px; font-weight: bold; font-size: 14px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)

        self.cancel_button = QPushButton("Скасувати")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #e0e0e0; color: #555555; padding: 10px 25px;
                border-radius: 6px; font-size: 14px;
            }
            QPushButton:hover { background-color: #d0d0d0; }
        """)

        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        self.setLayout(main_layout)

        # Сигнали
        self.search_input.textChanged.connect(self.filter_employees)
        self.ok_button.clicked.connect(self.accept_selection)
        self.cancel_button.clicked.connect(self.reject)
        self.table.itemDoubleClicked.connect(self.accept_selection)

        self.load_employees()

    def load_employees(self):
        response = ApiClient().get(self, self.api_url)
        if response and "employees" in response:
            self.employees = response["employees"]
        else:
            self.employees = []
        self.filtered_employees = self.employees.copy()
        self.update_table()

    def update_table(self):
        self.table.setRowCount(0)
        for emp in self.filtered_employees:
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            # Наповнюємо комірки
            self.table.setItem(row, 0, QTableWidgetItem(emp.get("name", "---")))
            self.table.setItem(row, 1, QTableWidgetItem(emp.get("position", "---")))
            self.table.setItem(row, 2, QTableWidgetItem(emp.get("phone", "-")))
            self.table.setItem(row, 3, QTableWidgetItem(emp.get("email", "-")))

    def filter_employees(self, text):
        search_text = text.lower()
        self.filtered_employees = [
            e for e in self.employees
            if search_text in e.get("name", "").lower() or 
               search_text in e.get("position", "").lower() or
               search_text in e.get("contacts", {}).get("phone", "").lower()
        ]
        self.update_table()

    def accept_selection(self):
        row = self.table.currentRow()
        if row >= 0:
            self.selected_employee = self.filtered_employees[row]
            self.accept()
        else:
            QMessageBox.warning(self, "Вибір", "Будь ласка, виберіть працівника з таблиці.")

    def get_selected_employee(self):
        return self.selected_employee