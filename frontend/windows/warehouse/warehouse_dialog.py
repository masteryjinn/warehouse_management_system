from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLineEdit, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt
from windows.employees.employee_select_dialog import EmployeeSelectDialog  # Імпортуйте ваш клас діалогу вибору працівника
from utils.load_styles import load_dialog_styles  # Імпортуйте функцію для завантаження стилів

class WarehouseDialog(QDialog):
    def __init__(self, warehouse=None):
        super().__init__()
        self.warehouse = warehouse
        self.setWindowTitle("Секція складу")
        self.setFixedSize(350, 400) # Трохи ширше для кращого вигляду
        self.setStyleSheet(load_dialog_styles())
        self.selected_employee_id = warehouse.get("employee_id") if warehouse else None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 25)
        layout.setSpacing(15)

        # Заголовок
        title = "Редагування секції" if self.warehouse else "Нова секція"
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)

        # Поля вводу з підписами
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Наприклад: Сектор А-1")
        self.add_labeled_widget(layout, "Назва секції:", self.name_input)

        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Наприклад: 2-й поверх, ряд 4")
        self.add_labeled_widget(layout, "Локація:", self.location_input)

        # Блок вибору працівника (Поле + Кнопка в одному рядку)
        employee_layout = QHBoxLayout()
        self.employee_input = QLineEdit()
        self.employee_input.setReadOnly(True)
        self.employee_input.setPlaceholderText("Оберіть зі списку...")
        self.employee_input.setStyleSheet("background-color: #f0f4f8; color: #7f8c8d;")
        
        self.select_btn = QPushButton("🔍") # Можна замінити на іконку
        self.select_btn.setFixedSize(40, 32)
        self.select_btn.clicked.connect(self.open_employee_dialog)
        self.select_btn.setStyleSheet("""
            QPushButton { background-color: #3498db; color: white; border-radius: 4px; font-size: 14px; }
            QPushButton:hover { background-color: #2980b9; }
        """)
        
        employee_layout.addWidget(self.employee_input)
        employee_layout.addWidget(self.select_btn)
        
        layout.addWidget(QLabel("Відповідальний:"))
        layout.addLayout(employee_layout)

        layout.addStretch()

        # Кнопки дій
        button_layout = QHBoxLayout()
        self.save_button = QPushButton("Зберегти")
        self.save_button.setFixedHeight(35)
        
        self.cancel_button = QPushButton("Скасувати")
        self.cancel_button.setObjectName("cancel_button") # Для твоїх стилів
        self.cancel_button.setFixedHeight(35)
        
        button_layout.addWidget(self.save_button)
        button_layout.addWidget(self.cancel_button)
        layout.addLayout(button_layout)

        # Сигнали
        self.save_button.clicked.connect(self.accept_with_validation)
        self.cancel_button.clicked.connect(self.reject)

        if self.warehouse:
            self.populate_fields()

    def add_labeled_widget(self, layout, label_text, widget):
        lbl = QLabel(label_text)
        lbl.setStyleSheet("font-weight: 500; color: #34495e;")
        layout.addWidget(lbl)
        layout.addWidget(widget)

    def open_employee_dialog(self):
        dialog = EmployeeSelectDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected = dialog.get_selected_employee()
            if selected:
                self.employee_input.setText(selected["name"])

    def populate_fields(self):
        self.name_input.setText(self.warehouse.get("name", ""))
        self.location_input.setText(self.warehouse.get("location", ""))
        self.employee_input.setText(self.warehouse.get("employee_name", ""))

    def accept_with_validation(self):
        name = self.name_input.text().strip()
        location = self.location_input.text().strip()
        employee = self.employee_input.text().strip()

        # Перевірка на порожні поля
        if not name:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть назву складу.")
            return

        if not location:
            QMessageBox.warning(self, "Помилка", "Будь ласка, введіть локацію складу.")
            return

        if not employee:
            QMessageBox.warning(self, "Помилка", "Будь ласка, виберіть відповідального працівника.")
            return

        self.accept()  # Усе добре — приймаємо форму

    def get_data(self):
        return {
            "name": self.name_input.text(),
            "location": self.location_input.text(),
            "employee_name": self.employee_input.text()
        }
