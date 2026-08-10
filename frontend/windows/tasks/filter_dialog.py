from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QLineEdit,
    QPushButton, QDateEdit, QCheckBox, QGridLayout, QFrame
)
from PyQt6.QtCore import QDate, Qt
from windows.employees.employee_select_dialog import EmployeeSelectDialog
from utils.load_styles import load_dialog_styles

class TaskFilterDialog(QDialog):
    def __init__(self, parent=None, last_filters=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 Фільтрація завдань")
        self.setFixedSize(500, 400) 
        self.selected_employee = None
        self.init_ui(last_filters)
    
    def init_ui(self, last_filters=None):
        self.setStyleSheet(load_dialog_styles())
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("Налаштування фільтрів завдань")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #1e3a5f; padding-bottom: 5px;")
        main_layout.addWidget(title_label)

        # Сітка параметрів
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1) # Дозволяє полям вводу розширюватися

        grid.addWidget(QLabel("Статус:"), 0, 0)
        self.status_combo = QComboBox()
        self.status_combo.addItems(["Усі", "Нове", "У процесі", "На перевірці", "Завершено", "Скасовано"])
        status_data = [None, "new", "in_progress", "under_review", "completed", "cancelled"]
        for i, data in enumerate(status_data): self.status_combo.setItemData(i, data)
        grid.addWidget(self.status_combo, 0, 1)

        grid.addWidget(QLabel("Пріоритет:"), 1, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(["Усі", "Низький", "Середній", "Високий"])
        priority_data = [None, "low", "medium", "high"]
        for i, data in enumerate(priority_data): self.priority_combo.setItemData(i, data)
        grid.addWidget(self.priority_combo, 1, 1)

        grid.addWidget(QLabel("Виконавець:"), 2, 0)
        emp_layout = QHBoxLayout()
        self.employee_input = QLineEdit()
        self.employee_input.setReadOnly(True)
        self.employee_input.setPlaceholderText("Оберіть працівника...")
        self.employee_btn = QPushButton("👥") 
        self.employee_btn.setFixedWidth(40)
        self.employee_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.employee_btn.clicked.connect(self.select_employee)
        emp_layout.addWidget(self.employee_input)
        emp_layout.addWidget(self.employee_btn)
        grid.addLayout(emp_layout, 2, 1)

        main_layout.addLayout(grid)

        # Секція Дедлайну
        deadline_frame = QFrame()
        deadline_frame.setObjectName("deadline_frame")
        deadline_frame.setStyleSheet("""
            #deadline_frame {
                background-color: #f8f9fa; 
                border-radius: 10px; 
                border: 1px solid #e0e0e0;
            }
        """)
        deadline_layout = QVBoxLayout(deadline_frame)
        deadline_layout.setContentsMargins(15, 10, 15, 15)
        
        self.filter_deadline = QCheckBox("Фільтрувати за дедлайном")
        self.filter_deadline.setStyleSheet("font-weight: bold; border: none; background: transparent;")
        deadline_layout.addWidget(self.filter_deadline)

        date_range_layout = QHBoxLayout()
        self.start_date = QDateEdit(QDate.currentDate().addMonths(-1))
        self.end_date = QDateEdit(QDate.currentDate().addMonths(1))
        
        for d in [self.start_date, self.end_date]:
            d.setCalendarPopup(True)
            d.setDisplayFormat("dd.MM.yyyy")
            # Прибираємо setFixedWidth, щоб текст не обрізався
            d.setMinimumWidth(140) 
        
        date_range_layout.addWidget(QLabel("з"))
        date_range_layout.addWidget(self.start_date)
        date_range_layout.addSpacing(10)
        date_range_layout.addWidget(QLabel("по"))
        date_range_layout.addWidget(self.end_date)
        date_range_layout.addStretch()
        
        deadline_layout.addLayout(date_range_layout)
        main_layout.addWidget(deadline_frame)

        # Додаємо розпірку перед кнопками
        main_layout.addStretch()

        # Кнопки дій
        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("✅ Застосувати")
        self.reset_btn = QPushButton("🔄 Скинути")
        self.cancel_btn = QPushButton("✖️ Скасувати")

        self.cancel_btn.setObjectName("cancel_button")
        
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.reset_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.setSpacing(15)
        main_layout.addLayout(btn_layout)

        # Логіка
        self.filter_deadline.toggled.connect(self.toggle_deadline_fields)
        self.apply_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.reset_btn.clicked.connect(self.reset_filters)

        self.toggle_deadline_fields(False)
        if last_filters: self.set_filters(last_filters)

    def toggle_deadline_fields(self, checked):
        self.start_date.setEnabled(checked)
        self.end_date.setEnabled(checked)

    def select_employee(self):
        dialog = EmployeeSelectDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_employee = dialog.get_selected_employee()
            if self.selected_employee:
                self.employee_input.setText(self.selected_employee["name"])

    def get_filters(self):
        return {
            "status": self.status_combo.currentData(),
            "priority": self.priority_combo.currentData(),
            "employee_id": self.selected_employee["employee_id"] if self.selected_employee else None,
            "employee_name": self.selected_employee["name"] if self.selected_employee else None,
            "start_date": self.start_date.date().toString("yyyy-MM-dd") if self.filter_deadline.isChecked() else None,
            "end_date": self.end_date.date().toString("yyyy-MM-dd") if self.filter_deadline.isChecked() else None
        }

    def set_filters(self, filters):
        if filters.get("status"):
            index = self.status_combo.findData(filters["status"])
            if index >= 0: self.status_combo.setCurrentIndex(index)
        if filters.get("priority"):
            index = self.priority_combo.findData(filters["priority"])
            if index >= 0: self.priority_combo.setCurrentIndex(index)
        if filters.get("employee_name"):
            self.selected_employee = {"employee_id": filters.get("employee_id"), "name": filters.get("employee_name")}
            self.employee_input.setText(self.selected_employee["name"])
        if filters.get("start_date"):
            self.start_date.setDate(QDate.fromString(filters["start_date"], "yyyy-MM-dd"))
            self.filter_deadline.setChecked(True)
        if filters.get("end_date"):
            self.end_date.setDate(QDate.fromString(filters["end_date"], "yyyy-MM-dd"))
            self.filter_deadline.setChecked(True)

    def reset_filters(self):
        self.status_combo.setCurrentIndex(0)
        self.priority_combo.setCurrentIndex(0)
        self.selected_employee = None
        self.employee_input.clear()
        self.start_date.setDate(QDate.currentDate().addMonths(-1))
        self.end_date.setDate(QDate.currentDate().addMonths(1))
        self.filter_deadline.setChecked(False)