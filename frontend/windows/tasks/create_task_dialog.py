from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QDialog, QLineEdit,
    QTextEdit, QComboBox, QDateTimeEdit, QSpinBox, QGridLayout
)
from PyQt6.QtCore import QDateTime, Qt
from utils.load_styles import load_dialog_styles

class CreateTaskDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📝 Створення завдання")
        self.setFixedSize(450, 530) # Фіксований розмір для стабільного вигляду
        
        self.priority_map = {
            "Низький": "low",
            "Середній": "medium",
            "Високий": "high"
        }
        
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_dialog_styles())
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # Заголовок
        title_label = QLabel("Створення нового завдання")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #1e3a5f; padding-bottom: 10px;")
        main_layout.addWidget(title_label)

        # Сітка для полів вводу
        grid = QGridLayout()
        grid.setSpacing(12)
        grid.setColumnStretch(1, 1)

        # Назва
        grid.addWidget(QLabel("Назва:"), 0, 0)
        self.title_edit = QLineEdit()
        self.title_edit.setPlaceholderText("Що потрібно зробити?")
        grid.addWidget(self.title_edit, 0, 1)

        # Пріоритет
        grid.addWidget(QLabel("Пріоритет:"), 1, 0)
        self.priority_combo = QComboBox()
        self.priority_combo.addItems(list(self.priority_map.keys()))
        grid.addWidget(self.priority_combo, 1, 1)

        # Кількість виконавців
        grid.addWidget(QLabel("Виконавців:"), 2, 0)
        self.max_assignees_spin = QSpinBox()
        self.max_assignees_spin.setRange(1, 50)
        self.max_assignees_spin.setValue(1)
        grid.addWidget(self.max_assignees_spin, 2, 1)

        # Дедлайн (Дата та Час)
        grid.addWidget(QLabel("Дедлайн:"), 3, 0)
        self.deadline_edit = QDateTimeEdit()
        self.deadline_edit.setCalendarPopup(True)
        self.deadline_edit.setDisplayFormat("dd.MM.yyyy HH:mm") # Формат дати та часу
        self.deadline_edit.setDateTime(QDateTime.currentDateTime().addDays(7))
        self.deadline_edit.setMinimumDateTime(QDateTime.currentDateTime())
        grid.addWidget(self.deadline_edit, 3, 1)

        main_layout.addLayout(grid)

        # Опис (виносимо окремо, бо він великий)
        main_layout.addWidget(QLabel("Опис завдання:"))
        self.description_edit = QTextEdit()
        self.description_edit.setFixedHeight(150)
        self.description_edit.setPlaceholderText("Деталі завдання...")
        main_layout.addWidget(self.description_edit)

        main_layout.addStretch()

        # Кнопки
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(15)
        
        self.create_btn = QPushButton("✅ Створити")
        # Якщо хочете ще менші кнопки, змініть height: 35px на 30px
        self.create_btn.setStyleSheet("background-color: #3498db; color: white; font-weight: bold;")
        
        self.cancel_btn = QPushButton("✖️ Скасувати")
        self.cancel_btn.setObjectName("cancel_button")
        
        btn_layout.addWidget(self.create_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addSpacing(15) # Додаємо відстань між кнопками
        main_layout.addLayout(btn_layout)

        # З'єднання сигналів
        self.create_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def get_task_data(self):
        # Повертаємо ISO формат для бази даних (yyyy-MM-dd HH:mm:ss)
        return {
            "title": self.title_edit.text().strip(),
            "description": self.description_edit.toPlainText().strip(),
            "priority": self.priority_map[self.priority_combo.currentText()],
            "deadline": self.deadline_edit.dateTime().toString("yyyy-MM-dd HH:mm:ss"),
            "max_assignees": self.max_assignees_spin.value()
        }