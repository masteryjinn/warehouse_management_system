from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QComboBox, QHBoxLayout, QMessageBox, QCheckBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator
from windows.suppliers.supplier_select_dialog import SupplierSelectDialog
import re
from services.api_client import ApiClient
from PyQt6.QtWidgets import QDateEdit
from PyQt6.QtCore import QDate
from utils.load_styles import load_dialog_styles  
from windows.products.description_dialog import DescriptionDialog  


from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel, QPushButton, 
    QComboBox, QHBoxLayout, QMessageBox, QCheckBox, QFrame, QDateEdit
)
from PyQt6.QtCore import Qt, QDate

class ProductDialog(QDialog):
    def __init__(self, product=None, api_url=None):
        super().__init__()
        self.product = product
        self.api_url = api_url
        self.categories = []
        self.description_data = ""
        self.setWindowTitle("🏷️ Товар: " + ("Редагування" if product else "Новий"))
        self.setFixedSize(400, 680) 
        self.setStyleSheet(load_dialog_styles())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # --- БЛОК 1: Основна інформація ---
        base_info_frame = QFrame()
        base_info_frame.setStyleSheet("background-color: #fdfdfd; border: 1px solid #e0e0e0; border-radius: 8px;")
        base_layout = QVBoxLayout(base_info_frame)

        title_label = QLabel("📝 Основні дані")
        title_label.setStyleSheet("font-weight: bold; color: #2c3e50; border: none; font-size: 15px;")
        base_layout.addWidget(title_label)

        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Назва товару")
        base_layout.addWidget(QLabel("Назва:"))
        base_layout.addWidget(self.name_input)

        # Рядок Ціна + Од. виміру
        price_unit_layout = QHBoxLayout()
        
        price_vbox = QVBoxLayout()
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setValidator(QDoubleValidator(0.01, 999999.99, 2))
        price_vbox.addWidget(QLabel("Ціна (₴):"))
        price_vbox.addWidget(self.price_input)
        
        unit_vbox = QVBoxLayout()
        self.unit_input = QComboBox()
        self.unit_input.addItems(["шт", "кг", "г", "л", "мл", "бокс", "набір"])
        unit_vbox.addWidget(QLabel("Одиниця:"))
        unit_vbox.addWidget(self.unit_input)
        
        price_unit_layout.addLayout(price_vbox)
        price_unit_layout.addLayout(unit_vbox)
        base_layout.addLayout(price_unit_layout)

        main_layout.addWidget(base_info_frame)

        # --- БЛОК 2: Класифікація та Постачальник ---
        category_frame = QFrame()
        category_frame.setStyleSheet("background-color: #f9f9f9; border: 1px solid #e0e0e0; border-radius: 8px;")
        cat_layout = QVBoxLayout(category_frame)

        cat_layout.addWidget(QLabel("📂 Категорія:"))
        self.category_input = QComboBox()
        cat_layout.addWidget(self.category_input)

        cat_layout.addWidget(QLabel("🤝 Постачальник:"))
        supplier_select_layout = QHBoxLayout()
        self.supplier_input = QLineEdit()
        self.supplier_input.setReadOnly(True)
        self.supplier_input.setPlaceholderText("Оберіть зі списку...")
        
        self.supplier_btn = QPushButton("🔍")
        self.supplier_btn.setFixedWidth(40)
        self.supplier_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.supplier_btn.clicked.connect(self.open_supplier_dialog)
        
        supplier_select_layout.addWidget(self.supplier_input)
        supplier_select_layout.addWidget(self.supplier_btn)
        cat_layout.addLayout(supplier_select_layout)

        main_layout.addWidget(category_frame)

        # --- БЛОК 3: Опис та Терміни ---
        extra_frame = QFrame()
        extra_frame.setStyleSheet("background-color: #ffffff; border: 1px solid #e0e0e0; border-radius: 8px;")
        extra_layout = QVBoxLayout(extra_frame)

        self.edit_description_button = QPushButton("📄 Редагувати опис товару")
        self.edit_description_button.setStyleSheet("""
        QPushButton {
            background-color: #3498db; 
            color: white; 
            font-weight: bold; 
            border-radius: 5px;
        }
        QPushButton:hover {
            background-color: #2980b9;
        }
        """)                             
        self.edit_description_button.clicked.connect(self.open_description_dialog)
        extra_layout.addWidget(extra_layout.addWidget(QLabel("Опис:")) or self.edit_description_button)

        # Термін придатності
        expiry_group = QVBoxLayout()
        self.expiry_checkbox = QCheckBox("Вказати термін придатності")
        self.expiry_date_input = QDateEdit()
        self.expiry_date_input.setCalendarPopup(True)
        self.expiry_date_input.setEnabled(False)
        self.expiry_date_input.setDate(QDate.currentDate().addDays(1))
        
        expiry_group.addWidget(self.expiry_checkbox)
        expiry_group.addWidget(self.expiry_date_input)
        extra_layout.addLayout(expiry_group)

        main_layout.addWidget(extra_frame)

        # --- Кнопки дій ---
        main_layout.addStretch()
        actions_layout = QHBoxLayout()
        self.save_button = QPushButton("💾 " + ("Зберегти зміни" if self.product else "Створити товар"))
        self.save_button.setMinimumHeight(45)
        
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.cancel_button.setObjectName("cancel_button")
        self.cancel_button.setMinimumHeight(45)

        actions_layout.addWidget(self.save_button)
        actions_layout.addWidget(self.cancel_button)
        main_layout.addLayout(actions_layout)

        # Логіка чекбокса
        self.expiry_checkbox.stateChanged.connect(
            lambda state: self.expiry_date_input.setEnabled(state == Qt.CheckState.Checked.value)
        )
        self.expiry_date_input.setMinimumDate(QDate.currentDate().addDays(1))
        self.expiry_date_input.setDisplayFormat("dd.MM.yyyy")
        
        self.save_button.clicked.connect(self.accept_with_validation)
        self.cancel_button.clicked.connect(self.reject)

        self.load_categories()
        if self.product:
            self.populate_fields()

    def open_description_dialog(self):
        dialog = DescriptionDialog(self.description_data)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.description_data = dialog.get_description()

    def load_categories(self):
        response = ApiClient().get(self, self.api_url + "/categories")
        if response and "categories" in response:
            self.categories = response["categories"]
            print("Завантажені категорії:", self.categories)  # Додайте цей рядок для перевірки
            self.category_input.clear()
            self.category_input.addItems(self.categories)
        else:
            QMessageBox.warning(self, "Помилка", "Не вдалося завантажити категорії.")

    def open_supplier_dialog(self):
        # Створюємо діалог для вибору постачальника
        dialog = SupplierSelectDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # Якщо користувач вибрав постачальника, відображаємо його в полі
            selected_supplier = dialog.get_selected_supplier()
            if selected_supplier:
                self.supplier_input.setText(selected_supplier["name"])

    def populate_fields(self):
        self.name_input.setText(self.product.get("name", ""))
        self.price_input.setText(str(self.product.get("price", "")))

        unit_value = self.product.get("unit", "")
        if unit_value in [self.unit_input.itemText(i) for i in range(self.unit_input.count())]:
            self.unit_input.setCurrentText(unit_value)
        else:
            self.unit_input.setCurrentText("шт")

        self.description_data = self.product.get("description", "")
        self.category_input.setCurrentText(self.product.get("category", ""))
        self.supplier_input.setText(self.product.get("supplier_name", ""))

        expiry_str = self.product.get("expiration_date", "")
        if expiry_str:
            # Пробуємо розпізнати європейський формат
            date = QDate.fromString(expiry_str, "dd.MM.yyyy")
            if not date.isValid():
                # Якщо не вийшло, пробуємо ISO формат (РРРР-ММ-ДД)
                date = QDate.fromString(expiry_str, Qt.DateFormat.ISODate)
            
            if date.isValid():
                self.expiry_date_input.setDate(date)
            self.expiry_checkbox.setChecked(True)
            self.expiry_date_input.setEnabled(True)
        else:
            self.expiry_checkbox.setChecked(False)
            self.expiry_date_input.setEnabled(False)


    def accept_with_validation(self):
        name = self.name_input.text().strip()
        price = self.price_input.text().strip()
        unit = self.unit_input.currentText().strip()
        description = self.description_data.strip()
        category = self.category_input.currentText().strip()
        supplier = self.supplier_input.text().strip()
        expiry_date = self.expiry_date_input.text().strip()

        # Перевірка на порожні поля
        if not name:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть назву продукту.")
            return

        if not price or not re.match(r'^\d+(\.\d{1,2})?$', price):
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть коректну ціну.")
            return
        
        # Перевірка що ціна > 0
        if float(price) <= 0:
            QMessageBox.warning(self, "Помилка", "Ціна повинна бути більшою за 0.")
            return

        if not unit:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть одиницю виміру.")
            return
        
        if not self.category_input.currentText():
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть категорію.")
            return

        if not supplier:
            QMessageBox.warning(self, "Помилка", "Будь ласка, оберіть постачальника.")
            return
        
        if self.expiry_checkbox.isChecked():
            selected_date = self.expiry_date_input.date()
            tomorrow = QDate.currentDate().addDays(1)
            if selected_date < tomorrow:
                QMessageBox.warning(self, "Помилка", "Термін придатності має бути щонайменше завтрашнім днем.")
                return

        self.accept() 

    def get_data(self):
        return{
            "name": self.name_input.text(),
            "price": float(self.price_input.text()),
            "unit": self.unit_input.currentText(),
            "description": self.description_data,
            "category": self.category_input.currentText(),
            "supplier_name": self.supplier_input.text(),
            "expiry_date": self.expiry_date_input.date().toString("yyyy-MM-dd") if self.expiry_checkbox.isChecked() else None
        }
