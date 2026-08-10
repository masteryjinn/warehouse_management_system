from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QComboBox,
    QPushButton, QHBoxLayout, QMessageBox
)
from utils.load_styles import load_dialog_styles
from PyQt6.QtCore import Qt

class UpdateRoleDialog(QDialog):
    def __init__(self, current_role):
        super().__init__()
        self.new_role = None
        self.current_role = current_role
        self.setWindowTitle("Налаштування доступу")
        self.setFixedSize(380, 280) # Фіксуємо розмір, щоб вікно не розтягувалося
        self.setStyleSheet(load_dialog_styles())

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(15)

        # Заголовок з іконкою
        title = QLabel("🔑 Зміна рівня доступу")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #1b263b;")
        layout.addWidget(title)

        # Інфо-блок про поточну роль
        roles_display = {
            "admin": "Адміністратор",
            "manager": "Менеджер",
            "employee": "Працівник"
        }
        current_text = roles_display.get(self.current_role, "Невідомо")
        
        info_label = QLabel(f"Поточна роль: <b>{current_text}</b>")
        info_label.setStyleSheet("color: #7f8c8d; font-size: 13px; background: #f8f9fa; padding: 5px; border-radius: 4px;")
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(info_label)

        # Випадаючий список
        layout.addWidget(QLabel("<b>Оберіть нову роль:</b>"))
        self.role_combo = QComboBox()
        
        # Додаємо елементи: Текст для UI + Технічне значення (UserRole)
        self.role_combo.addItem("Адміністратор", "admin")
        self.role_combo.addItem("Менеджер", "manager")
        self.role_combo.addItem("Працівник", "employee")
        
        # Встановлюємо поточну роль
        index = self.role_combo.findData(self.current_role)
        if index != -1:
            self.role_combo.setCurrentIndex(index)
            
        self.role_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #d1d9e6;
                border-radius: 6px;
                background: white;
            }
            QComboBox:focus { border-color: #3498db; }
        """)
        layout.addWidget(self.role_combo)

        layout.addStretch() # Відступ перед кнопками

        # Кнопки
        button_layout = QHBoxLayout()
        self.update_btn = QPushButton("💾 Оновити роль")
        self.update_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; 
                font-weight: bold; padding: 10px; border-radius: 6px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        
        self.cancel_btn = QPushButton("✖️ Скасувати")
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.setStyleSheet("padding: 10px;")
        
        button_layout.addWidget(self.update_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        # Сигнали
        self.update_btn.clicked.connect(self.update_role)
        self.cancel_btn.clicked.connect(self.reject)

    def update_role(self):
        # Дістаємо технічне значення (admin/manager/employee) з userData
        self.new_role = self.role_combo.currentData()
        
        if self.new_role == self.current_role:
            QMessageBox.warning(self, "Увага", "Ця роль вже встановлена для працівника.")
            return
            
        self.accept()

    def get_new_role(self):
        return self.new_role