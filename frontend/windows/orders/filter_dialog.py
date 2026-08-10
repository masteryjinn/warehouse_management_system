from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QCheckBox,
    QPushButton, QDateEdit, QMessageBox, QFrame
)
from PyQt6.QtCore import Qt, QDate
from windows.customers.customer_select_dialog import CustomerSelectDialog
from utils.load_styles import load_dialog_styles

class FilterDialog(QDialog):
    def __init__(self, parent=None, current_filters=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Фільтр замовлень")
        self.setFixedSize(420, 470) # Оптимізували висоту
        self.current_filters = current_filters or {}
        self.status_map = {
                "Чернетка": "draft",
                "Нове (Очікує)": "new",
                "В обробці (Збирається)": "collecting",
                "Перевірка пакування": "review_pack",
                "Упаковано (Готове)": "packed",
                "Відправлено": "shipped",
                "Очікує розпакування": "restocking",
                "В обробці (Розпаковується)": "unpacking",
                "Перевірка повернення": "review_restock",
                "Скасовано": "cancelled"
            }
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_dialog_styles())
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # 1. Заголовок
        title_label = QLabel("Налаштування фільтрів")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        main_layout.addWidget(title_label)

        # 2. Блок Клієнта (як у вікні створення замовлення)
        customer_layout = QVBoxLayout()
        customer_layout.setSpacing(5)
        customer_layout.addWidget(QLabel("👤 Клієнт:"))
        
        cust_input_layout = QHBoxLayout()
        self.customer_input = QLineEdit()
        self.customer_input.setReadOnly(True)
        self.customer_input.setPlaceholderText("Оберіть клієнта для фільтрації...")
        
        self.customer_button = QPushButton("🔍")
        self.customer_button.setFixedWidth(45)
        self.customer_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.customer_button.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        
        cust_input_layout.addWidget(self.customer_input)
        cust_input_layout.addWidget(self.customer_button)
        customer_layout.addLayout(cust_input_layout)
        main_layout.addLayout(customer_layout)

        # 3. Статус
        status_layout = QVBoxLayout()
        status_layout.setSpacing(5)
        status_layout.addWidget(QLabel("📋 Статус замовлення:"))
        self.sort_combo = QComboBox()
        self.sort_combo.addItems(["Усі"] + list(self.status_map.keys()))
        status_layout.addWidget(self.sort_combo)
        main_layout.addLayout(status_layout)

        # 4. Блок Дати (Картка)
        date_frame = QFrame()
        date_frame.setStyleSheet("""
            QFrame { background-color: #f8f9fa; border: 1px solid #dee2e6; border-radius: 10px; }
            QLabel { border: none; font-weight: bold; }
            QCheckBox {background-color: #f8f9fa;}
        """)
        date_layout = QVBoxLayout(date_frame)
        
        self.date_filter_checkbox = QCheckBox("Фільтрувати за датою")
        self.date_filter_checkbox.setStyleSheet("font-weight: bold; color: #34495e;")
        date_layout.addWidget(self.date_filter_checkbox)

        dates_row = QHBoxLayout()
        # Мінімальна дата
        v_box_min = QVBoxLayout()
        v_box_min.addWidget(QLabel("З:"))
        self.date_min_input = QDateEdit(calendarPopup=True)
        self.date_min_input.setDate(QDate.currentDate().addMonths(-1))
        v_box_min.addWidget(self.date_min_input)
        
        # Максимальна дата
        v_box_max = QVBoxLayout()
        v_box_max.addWidget(QLabel("По:"))
        self.date_max_input = QDateEdit(calendarPopup=True)
        self.date_max_input.setDate(QDate.currentDate())
        v_box_max.addWidget(self.date_max_input)
        
        dates_row.addLayout(v_box_min)
        dates_row.addLayout(v_box_max)
        date_layout.addLayout(dates_row)
        main_layout.addWidget(date_frame)

        main_layout.addStretch()

        # 5. Кнопки дій
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("✅ Застосувати")
        self.apply_button.setMinimumHeight(40)
        
        self.clear_button = QPushButton("🔄 Скинути")
        self.clear_button.setMinimumHeight(40)
        
        self.cancel_button = QPushButton("Скасувати")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setMinimumHeight(40)

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.cancel_button)
        main_layout.addLayout(button_layout)

        # Зв'язки
        self.customer_button.clicked.connect(self.open_customer_dialog)
        self.date_filter_checkbox.stateChanged.connect(self.toggle_date_inputs)
        self.apply_button.clicked.connect(self.validate_and_accept)
        self.clear_button.clicked.connect(self.clear_fields)
        self.cancel_button.clicked.connect(self.reject)

        self.load_current_filters()

    def toggle_date_inputs(self):
        enabled = self.date_filter_checkbox.isChecked()
        self.date_min_input.setEnabled(enabled)
        self.date_max_input.setEnabled(enabled)

    def open_customer_dialog(self):
        dialog = CustomerSelectDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_customer = dialog.get_selected_customer()
            if selected_customer:
                self.customer_input.setText(selected_customer["name"])

    def validate_and_accept(self):
        # Перевірка діапазону дат
        if self.date_filter_checkbox.isChecked():
            if self.date_min_input.date() > self.date_max_input.date():
                QMessageBox.warning(self, "Помилка", "Мінімальна дата не може бути пізніше за максимальну.")
                return
        
        if not self.customer_input:
            QMessageBox.warning(self, "Помилка", "Поле клієнта обов'язкове для заповнення.")
            return

        self.accept()

    def get_filters(self):
        filters = {}

        if self.date_filter_checkbox.isChecked():
            filters["date_min"] = self.date_min_input.date().toString("yyyy-MM-dd") + " 00:00:00"
            filters["date_max"] = self.date_max_input.date().toString("yyyy-MM-dd") + " 23:59:59"

        status_ukr = self.sort_combo.currentText()
        if status_ukr:
            filters["status_filter"] = self.status_map.get(status_ukr, "")


        customer_name = self.customer_input.text()
        if customer_name:
            filters["customer_name_filter"] = customer_name

        return filters

    def load_current_filters(self):
        self.customer_input.setText(self.current_filters.get("customer_name_filter", ""))

        date_min = self.current_filters.get("date_min")
        date_max = self.current_filters.get("date_max")
        if date_min and date_max:
            self.date_filter_checkbox.setChecked(True)
            self.date_min_input.setDate(QDate.fromString(date_min, "yyyy-MM-dd"))
            self.date_max_input.setDate(QDate.fromString(date_max, "yyyy-MM-dd"))
        else:
            self.date_filter_checkbox.setChecked(False)
            self.toggle_date_inputs()

        status_eng = self.current_filters.get("status_filter", "")
        # Пошук українського еквіваленту
        status_ukr = next((k for k, v in self.status_map.items() if v == status_eng), "")
        index = self.sort_combo.findText(status_ukr)
        self.sort_combo.setCurrentIndex(index if index >= 0 else 0)


    def clear_fields(self):
        self.sort_combo.setCurrentIndex(0)
        self.customer_input.clear()
        self.date_min_input.setDate(QDate.currentDate().addMonths(-1))
        self.date_max_input.setDate(QDate.currentDate())
        self.date_filter_checkbox.setChecked(False)
