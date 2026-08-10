from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, 
    QSpinBox, QCheckBox, QMessageBox, QDateEdit, QFrame, QGridLayout, QLineEdit
)
from PyQt6.QtCore import QDate, Qt
from services.api_client import ApiClient
from windows.products.product_select_dialog import ProductSelectDialog
from utils.load_styles import load_dialog_styles
from config.config import API_URL

class StockMovementFilterDialog(QDialog):
    def __init__(self, parent=None, current_filters=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Фільтр руху товарів")
        self.setFixedSize(500, 520)  # Трохи збільшив висоту для комфорту
        self.current_filters = current_filters or {}
        self.sections = []
        
        # Сховище для вибраного товару
        self.selected_product_data = None 

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_dialog_styles())
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        title_label = QLabel("Налаштування фільтрації")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a5f; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # --- Блок 1: Продукт та Секція ---
        top_frame = QFrame()
        top_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa; 
                border-radius: 10px; 
                border: 1px solid #e0e0e0;
            }
            QLabel { border: none; background: transparent; font-weight: bold; }
        """)
        top_layout = QGridLayout(top_frame)
        top_layout.setContentsMargins(15, 15, 15, 15)
        top_layout.setSpacing(10)

        # Вибір продукту
        top_layout.addWidget(QLabel("Продукт:"), 0, 0)
        prod_h_layout = QHBoxLayout()
        
        self.product_display = QLineEdit()
        self.product_display.setReadOnly(True)
        self.product_display.setPlaceholderText("Усі товари")
        self.product_display.setStyleSheet("""
            QLineEdit {
                background-color: #e9ecef; 
                color: #212529; 
                border: 1px solid #ced4da;
                padding: 6px;
                border-radius: 4px;
            }
        """)
        
        self.product_search_button = QPushButton("🔍")
        self.product_search_button.setFixedWidth(40)
        self.product_search_button.setToolTip("Відкрити пошук товарів")
        
        self.product_clear_button = QPushButton("🗑️")
        self.product_clear_button.setFixedWidth(40)
        self.product_clear_button.setToolTip("Скинути вибір товару")
        
        prod_h_layout.addWidget(self.product_display)
        prod_h_layout.addWidget(self.product_search_button)
        prod_h_layout.addWidget(self.product_clear_button)
        top_layout.addLayout(prod_h_layout, 0, 1)

        # Вибір секції
        top_layout.addWidget(QLabel("Секція:"), 1, 0)
        self.section_combo = QComboBox()
        top_layout.addWidget(self.section_combo, 1, 1)

        main_layout.addWidget(top_frame)

        # --- Блок 2: Дати ---
        date_frame = QFrame()
        date_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 10px; border: 1px solid #e0e0e0;")
        date_layout = QVBoxLayout(date_frame)
        date_layout.setContentsMargins(15, 10, 15, 15)
        
        self.use_date_filter_checkbox = QCheckBox("Фільтрувати за датою")
        self.use_date_filter_checkbox.setStyleSheet("font-weight: bold; border: none;")
        date_layout.addWidget(self.use_date_filter_checkbox)

        date_pickers = QHBoxLayout()
        self.date_from = QDateEdit(calendarPopup=True)
        self.date_to = QDateEdit(calendarPopup=True)
        for d in [self.date_from, self.date_to]:
            d.setDate(QDate.currentDate())
            d.setDisplayFormat("dd.MM.yyyy")
            d.setFixedWidth(130)
        
        date_pickers.addWidget(QLabel("з"))
        date_pickers.addWidget(self.date_from)
        date_pickers.addSpacing(10)
        date_pickers.addWidget(QLabel("по"))
        date_pickers.addWidget(self.date_to)
        date_pickers.addStretch()
        date_layout.addLayout(date_pickers)
        main_layout.addWidget(date_frame)

        # --- Блок 3: Кількість ---
        qty_frame = QFrame()
        qty_frame.setStyleSheet("background-color: #f8f9fa; border-radius: 10px; border: 1px solid #e0e0e0;")
        qty_layout = QVBoxLayout(qty_frame)
        qty_layout.setContentsMargins(15, 10, 15, 15)

        self.use_quantity_filter_checkbox = QCheckBox("Фільтрувати за кількістю")
        self.use_quantity_filter_checkbox.setStyleSheet("font-weight: bold; border: none;")
        qty_layout.addWidget(self.use_quantity_filter_checkbox)

        qty_spins = QHBoxLayout()
        self.quantity_min_spin = QSpinBox()
        self.quantity_max_spin = QSpinBox()
        for s in [self.quantity_min_spin, self.quantity_max_spin]:
            s.setRange(0, 1000000)
            s.setFixedWidth(100)
        
        qty_spins.addWidget(QLabel("від"))
        qty_spins.addWidget(self.quantity_min_spin)
        qty_spins.addSpacing(10)
        qty_spins.addWidget(QLabel("до"))
        qty_spins.addWidget(self.quantity_max_spin)
        qty_spins.addStretch()
        qty_layout.addLayout(qty_spins)
        main_layout.addWidget(qty_frame)

        main_layout.addStretch()

        # --- Кнопки дій ---
        button_layout = QHBoxLayout()
        self.apply_button = QPushButton("✅ Застосувати")
        self.clear_button = QPushButton("🔄 Скинути все")
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.cancel_button.setObjectName("cancel_button")

        button_layout.addWidget(self.apply_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addWidget(self.cancel_button)
        button_layout.setSpacing(10)
        main_layout.addLayout(button_layout)

        # Сигнали
        self.product_search_button.clicked.connect(self.open_product_search)
        self.product_clear_button.clicked.connect(self.clear_product_selection)
        self.apply_button.clicked.connect(self.validate_and_accept)
        self.clear_button.clicked.connect(self.clear_all_fields)
        self.cancel_button.clicked.connect(self.reject)
        self.use_date_filter_checkbox.toggled.connect(self.toggle_date_fields)
        self.use_quantity_filter_checkbox.toggled.connect(self.toggle_quantity_fields)

        # Початковий стан
        self.toggle_date_fields(False)
        self.toggle_quantity_fields(False)

    def showEvent(self, event):
        super().showEvent(event)
        self.load_options()

    def toggle_date_fields(self, checked):
        self.date_from.setEnabled(checked)
        self.date_to.setEnabled(checked)

    def toggle_quantity_fields(self, checked):
        self.quantity_min_spin.setEnabled(checked)
        self.quantity_max_spin.setEnabled(checked)

    def clear_product_selection(self):
        self.selected_product_data = None
        self.product_display.clear()
        self.product_display.setPlaceholderText("Усі товари")

    def open_product_search(self):
        dialog = ProductSelectDialog(available_only=False)
        if dialog.exec():
            selected = dialog.get_selected_product()
            if selected:
                self.selected_product_data = {
                    "id": selected["product_id"],
                    "name": selected["name"]
                }
                self.product_display.setText(f"{selected['name']}")

    def load_options(self):
        response = ApiClient().get(self, API_URL + "/sections/full")
        if response and "data" in response:
            self.sections = response["data"]
            self.section_combo.clear()
            self.section_combo.addItem("Всі секції", None)
            for section in self.sections:
                self.section_combo.addItem(section["name"], section["section_id"])
        
        # Після завантаження опцій секцій, завантажуємо поточні фільтри
        self.load_current_filters()

    def load_current_filters(self):
        if not self.current_filters: return
        
        # 1. Товар
        p_id = self.current_filters.get("product_id")
        p_name = self.current_filters.get("name")
        if p_id and p_name:
            self.selected_product_data = {"id": p_id, "name": p_name}
            self.product_display.setText(p_name)

        # 2. Секція
        s_id = self.current_filters.get("section_id")
        if s_id:
            idx = self.section_combo.findData(s_id)
            if idx != -1: self.section_combo.setCurrentIndex(idx)

        # 3. Дати
        if "date_from" in self.current_filters:
            self.date_from.setDate(QDate.fromString(self.current_filters["date_from"], "yyyy-MM-dd"))
            self.date_to.setDate(QDate.fromString(self.current_filters["date_to"], "yyyy-MM-dd"))
            self.use_date_filter_checkbox.setChecked(True)

        # 4. Кількість
        if "quantity_min" in self.current_filters:
            self.quantity_min_spin.setValue(self.current_filters["quantity_min"])
            self.quantity_max_spin.setValue(self.current_filters.get("quantity_max", 0))
            self.use_quantity_filter_checkbox.setChecked(True)

    def validate_and_accept(self):
        if self.use_date_filter_checkbox.isChecked():
            if self.date_from.date() > self.date_to.date():
                QMessageBox.warning(self, "Помилка", "Дата 'з' не може бути пізніше за дату 'по'.")
                return
        
        if self.use_quantity_filter_checkbox.isChecked():
            if self.quantity_max_spin.value() > 0 and self.quantity_min_spin.value() > self.quantity_max_spin.value():
                QMessageBox.warning(self, "Помилка", "Мінімальна кількість не може бути більшою за максимальну.")
                return
        self.accept()

    def get_filters(self):
        filters = {}
        
        if self.selected_product_data:
            filters["product_id"] = self.selected_product_data["id"]
            filters["name"] = self.selected_product_data["name"]
            
        if self.section_combo.currentData():
            filters["section_id"] = self.section_combo.currentData()
            
        if self.use_date_filter_checkbox.isChecked():
            filters["date_from"] = self.date_from.date().toString("yyyy-MM-dd")
            filters["date_to"] = self.date_to.date().toString("yyyy-MM-dd")
            
        if self.use_quantity_filter_checkbox.isChecked():
            filters["quantity_min"] = self.quantity_min_spin.value()
            if self.quantity_max_spin.value() > 0:
                filters["quantity_max"] = self.quantity_max_spin.value()
                
        return filters

    def clear_all_fields(self):
        """Повне скидання всіх налаштувань фільтра"""
        self.clear_product_selection()
        self.section_combo.setCurrentIndex(0)
        self.use_date_filter_checkbox.setChecked(False)
        self.use_quantity_filter_checkbox.setChecked(False)
        self.date_from.setDate(QDate.currentDate())
        self.date_to.setDate(QDate.currentDate())
        self.quantity_min_spin.setValue(0)
        self.quantity_max_spin.setValue(0)