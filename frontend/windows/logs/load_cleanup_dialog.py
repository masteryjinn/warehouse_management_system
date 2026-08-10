from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton, 
    QCheckBox, QComboBox, QHBoxLayout, QFrame, QDateEdit
)
from PyQt6.QtCore import Qt, QDate
from utils.load_styles import load_dialog_styles

class LogCleanupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Адміністрування логів")
        self.setFixedSize(420, 550)
        self.setStyleSheet(load_dialog_styles())

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(25, 25, 25, 25)

        # Заголовок
        header = QLabel("🗑️ Очищення історії подій")
        header.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)

        # Інфо-блок
        info = QLabel("Оберіть тип даних та часовий проміжок для видалення.")
        info.setWordWrap(True)
        info.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 10px;")
        layout.addWidget(info)

        # Тип логів
        layout.addWidget(QLabel("<b>Тип даних:</b>"))
        self.log_type_combo = QComboBox()
        self.log_type_combo.addItems(["Журнал сесій(входи/виходи)", "Дії користувачів"])
        layout.addWidget(self.log_type_combo)

        # Вибір періоду
        layout.addWidget(QLabel("<b>Період очищення:</b>"))
        range_layout = QHBoxLayout()
        
        self.date_from = QDateEdit()
        self.date_from.setCalendarPopup(True)
        self.date_from.setDate(QDate.currentDate().addMonths(-1))
        
        self.date_to = QDateEdit()
        self.date_to.setCalendarPopup(True)
        self.date_to.setDate(QDate.currentDate())
        
        range_layout.addWidget(QLabel("з"))
        range_layout.addWidget(self.date_from)
        range_layout.addWidget(QLabel("по"))
        range_layout.addWidget(self.date_to)
        range_layout.addStretch()
        layout.addLayout(range_layout)

        # Чекбокси
        self.all_dates_checkbox = QCheckBox("Видалити всі записи (ігнорувати дати)")
        self.all_dates_checkbox.stateChanged.connect(self.toggle_date_selection)
        layout.addWidget(self.all_dates_checkbox)

        self.archive_checkbox = QCheckBox("Архівувати перед видаленням")
        self.archive_checkbox.setChecked(True)
        layout.addWidget(self.archive_checkbox)

        # Розділювач
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        layout.addWidget(line)

        # Пароль
        layout.addWidget(QLabel("<b>Підтвердження паролем:</b>"))
        self.input = QLineEdit()
        self.input.setEchoMode(QLineEdit.EchoMode.Password)
        self.input.setPlaceholderText("Пароль адміністратора")
        layout.addWidget(self.input)

        self.show_pass_check = QCheckBox("Показати пароль")
        self.show_pass_check.stateChanged.connect(self.toggle_password_visibility)
        layout.addWidget(self.show_pass_check)

        # Кнопка дії
        self.button = QPushButton("🧹 Очистити обрані записи")
        self.button.clicked.connect(self.accept)
        layout.addWidget(self.button)

    def toggle_password_visibility(self):
        mode = QLineEdit.EchoMode.Normal if self.show_pass_check.isChecked() else QLineEdit.EchoMode.Password
        self.input.setEchoMode(mode)

    def toggle_date_selection(self):
        is_all = self.all_dates_checkbox.isChecked()
        self.date_from.setEnabled(not is_all)
        self.date_to.setEnabled(not is_all)

    def get_values(self):
        # Мапінг для зручного API-запиту
        log_map = {"Журнал сесій(входи/виходи)": "login", "Дії користувачів": "actions"}
        return {
            "password": self.input.text(),
            "log_type": log_map.get(self.log_type_combo.currentText(), "login"),
            "clear_all_dates": self.all_dates_checkbox.isChecked(),
            "date_from": self.date_from.date().toString("yyyy-MM-dd"),
            "date_to": self.date_to.date().toString("yyyy-MM-dd"),
            "include_archives": self.archive_checkbox.isChecked()
        }