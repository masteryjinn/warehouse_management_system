from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFrame
)
from PyQt6.QtCore import Qt
import tempfile
import webbrowser
from services.api_client import ApiClient
from utils import load_styles

class OrderDetailsDialog(QDialog):
    def __init__(self, order_id, api_url, is_employee=False):
        super().__init__()
        self.setWindowTitle("📄 Деталі замовлення")
        self.setMinimumSize(800, 500)
        self.order_id = order_id
        self.api_url = api_url
        self.is_employee = is_employee
        self.order_details = self.fetch_order_details(self.order_id)
        
        self.setStyleSheet(load_styles())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # 1. Верхня панель (Заголовок та Статус)
        header_layout = QHBoxLayout()
        
        title_container = QVBoxLayout()
        self.order_label = QLabel(f"Замовлення №{self.order_id}")
        self.order_label.setStyleSheet("font-size: 22px; font-weight: bold; color: #2c3e50;")
        
        self.status_label = QLabel("⚠️ Тільки перегляд")
        self.status_label.setStyleSheet("""
            color: #d35400; font-size: 13px; font-weight: bold;
            background-color: #fef0e1; padding: 4px 12px; border-radius: 12px;
        """)
        title_container.addWidget(self.order_label)
        title_container.addWidget(self.status_label)
        
        header_layout.addLayout(title_container)
        header_layout.addStretch()
        
        # Кнопка накладної зверху (як основна дія)
        if not self.is_employee:
            self.open_invoice_btn = QPushButton("📑 Відкрити накладну")
            self.open_invoice_btn.setMinimumHeight(40)
            self.open_invoice_btn.setMinimumWidth(200)
            self.open_invoice_btn.clicked.connect(self.open_invoice)
            header_layout.addWidget(self.open_invoice_btn)
        
        main_layout.addLayout(header_layout)

        # 2. Таблиця
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Назва", "Кількість", "Од.", "Ціна/шт", "Сума", "Секція"])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        for i in range(1, 6):
            header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)
            
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        main_layout.addWidget(self.table)

        # 3. Нижня панель (Сума та Закриття)
        footer_layout = QHBoxLayout()
        
        # Спеціальний фрейм для суми (як у попередньому вікні)
        self.total_frame = QFrame()
        total_inner_layout = QHBoxLayout(self.total_frame)
        
        self.total_label = QLabel("Загальна сума: 0.00 грн")
        self.total_label.setStyleSheet("""font-size: 20px; 
            font-weight: bold; 
            color: #57a9b5; 
            background: #f0f0f0; 
            padding: 10px 20px; 
            border-radius: 5px;
        """)
        total_inner_layout.addWidget(self.total_label)
        
        footer_layout.addWidget(self.total_frame)
        footer_layout.addStretch()

        #self.close_button = QPushButton("❌ Закрити")
        #self.close_button.setMinimumHeight(45)
        #self.close_button.setMinimumWidth(120)
        #self.close_button.setStyleSheet("background-color: #ecf0f1; color: #7f8c8d; font-weight: bold;")
        #self.close_button.clicked.connect(self.accept)
        
        #footer_layout.addWidget(self.close_button)
        main_layout.addLayout(footer_layout)

        # Помилка завантаження (якщо є)
        if not self.order_details:
            self.show_error_message()

        self.populate_table()

    def show_error_message(self):
        error_box = QLabel("❌ Помилка завантаження даних замовлення.")
        error_box.setStyleSheet("""
            background-color: #fdecea; color: #c0392b; padding: 15px;
            border-radius: 8px; border: 1px solid #e0b4b4;
        """)
        self.layout().insertWidget(2, error_box)
        self.open_invoice_btn.setEnabled(False)

    def populate_table(self):
        if not self.order_details:
            return

        total_sum = 0.0
        self.table.setRowCount(0)

        for detail in self.order_details:
            row = self.table.rowCount()
            self.table.insertRow(row)

            # Назва (ліворуч)
            self.table.setItem(row, 0, QTableWidgetItem(str(detail.get("product_name", ""))))
            
            # Числові дані (центр)
            cols = [
                str(detail.get("quantity", 0)),
                str(detail.get("unit", "")),
                f"{detail.get('price', 0):.2f}",
                f"{detail.get('line_total', 0):.2f}",
                str(detail.get("section_name", "-"))
            ]
            
            for i, text in enumerate(cols, 1):
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, i, item)

            total_sum += detail.get('line_total', 0)

        self.total_label.setText(f"Загальна сума замовлення: {total_sum:.2f} грн")

    def fetch_order_details(self, order_id):
        result = ApiClient.get(self, f"{self.api_url}/{order_id}/details")
        return result

    def fetch_invoice_pdf(self):
        result = ApiClient.get_file(self, f"{self.api_url}/{self.order_id}/invoice")
        return result

    def open_invoice(self):
        try:
            pdf_data = self.fetch_invoice_pdf()
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            tmp_file.write(pdf_data)
            tmp_file.close()
            webbrowser.open(tmp_file.name)  # відкриває у системному PDF-переглядачі
        except Exception as e:
            QMessageBox.critical(self, "Помилка", str(e))
