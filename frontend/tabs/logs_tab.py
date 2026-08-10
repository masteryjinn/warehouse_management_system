from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QComboBox,
                                QDateEdit, QLineEdit, QPushButton,
                                QTableWidget, QTableWidgetItem, QLabel, QMessageBox)
from PyQt6.QtCore import QDate, Qt
from windows.logs.load_cleanup_dialog import LogCleanupDialog
from config.config import API_URL
from services.api_client import ApiClient
from utils import load_styles, format_date, fade_in_widget

class LogsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_logs()

    def init_ui(self):
        self.setStyleSheet(load_styles())
        layout = QVBoxLayout()

        # Верхній ряд
        top_layout = QHBoxLayout()

        # Тип логів
        self.combo = QComboBox()
        self.combo.addItems(["Журнал сесій", "Дії користувачів"])
        self.combo.setItemData(0, "login")
        self.combo.setItemData(1, "actions")
        self.combo.currentIndexChanged.connect(self.load_logs)

        # Дата
        self.date_picker = QDateEdit()
        self.date_picker.setCalendarPopup(True)
        self.date_picker.setDisplayFormat("dd.MM.yyyy")
        self.date_picker.setDate(QDate.currentDate())
        self.date_picker.setMaximumDate(QDate.currentDate())
        self.date_picker.dateChanged.connect(self.load_logs)

        # Обмеження рядків
        self.row_limit_selector = QComboBox()
        self.row_limit_selector.addItems(["100", "500", "1000", "2000", "5000"])
        self.row_limit_selector.currentTextChanged.connect(self.load_logs)

        # Пошук
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по повідомленням...")

        # Кнопки
        search_btn = QPushButton("🔍 Пошук")
        search_btn.clicked.connect(self.load_logs)

        reset_btn = QPushButton("♻️ Скинути")
        reset_btn.clicked.connect(self.reset_filters)

        clear_btn = QPushButton("🗑️ Очистити логи")
        clear_btn.clicked.connect(self.clear_logs)

        # Додавання до layout
        top_layout.addWidget(QLabel("Тип:"))
        top_layout.addWidget(self.combo)
        top_layout.addWidget(QLabel("Дата:"))
        top_layout.addWidget(self.date_picker)
        top_layout.addWidget(QLabel("Рядків:"))
        top_layout.addWidget(self.row_limit_selector)
        top_layout.addWidget(self.search_input)
        top_layout.addWidget(search_btn)
        top_layout.addWidget(reset_btn)
        top_layout.addWidget(clear_btn)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Час", "Рівень", "Повідомлення"])
        #self.table.setWordWrap(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSortingEnabled(True)

        layout.addLayout(top_layout)
        layout.addWidget(self.table)

        self.setLayout(layout)

    def reset_filters(self):
        self.search_input.clear()
        self.date_picker.setDate(QDate.currentDate())
        self.combo.setCurrentIndex(0)
        self.row_limit_selector.setCurrentIndex(0)
        self.load_logs()

    def load_logs(self):
        log_type = self.combo.currentData()
        search_text = self.search_input.text().strip().lower()
        if log_type not in ["login", "actions"]:
            return

        params = {
            "log_type": log_type,
            "lines": self.row_limit_selector.currentText(),
            "log_date": self.date_picker.date().toString("yyyy-MM-dd")
        }

        # Викликаємо ApiClient, передаючи чистий URL та словник params
        result = ApiClient.get(self, f"{API_URL}/logs", params=params)
        if result:
            log_text = result.get("logs", "")
            self.populate_table(log_text, search_text)
        else:
            self.table.setRowCount(0)

    def populate_table(self, log_text: str, search_filter: str = ""):
        self.table.setRowCount(0)
        if not log_text.strip():
            return

        rows = []
        lines = log_text.strip().splitlines()

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Спроба розбити рядок за форматом: Час | Рівень | Повідомлення
            parts = line.split(" | ", 2)
            
            if len(parts) == 3:
                # Це стандартний рядок логу
                time_str, level, message = parts
                if search_filter and search_filter not in message.lower():
                    continue
                rows.append((time_str, level, message, False))
            else:
                # Це системне повідомлення від бекенду (наприклад, "Записів не знайдено")
                # Виводимо його, ігноруючи фільтр пошуку, щоб адмін бачив статус
                rows.append(("-", "INFO", line, True))

        self.table.setRowCount(len(rows))
        
        for row_idx, (time_str, level, message, is_system_msg) in enumerate(rows):
            # Створюємо елементи
            time_item = QTableWidgetItem(format_date(time_str, show_time=True) if time_str != "-" else "-")
            level_item = QTableWidgetItem(level)
            msg_item = QTableWidgetItem(message)

            # Вирівнювання
            time_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            level_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Стилізація залежно від типу повідомлення
            if is_system_msg:
                # Сірий колір для системних повідомлень
                msg_item.setForeground(Qt.GlobalColor.gray)
                level_item.setForeground(Qt.GlobalColor.gray)
            else:
                # Кольори для рівнів важливості
                if level == "ERROR":
                    level_item.setForeground(Qt.GlobalColor.red)
                elif level == "WARNING":
                    level_item.setForeground(Qt.GlobalColor.darkYellow)
                elif level == "INFO":
                    level_item.setForeground(Qt.GlobalColor.darkBlue)

            self.table.setItem(row_idx, 0, time_item)
            self.table.setItem(row_idx, 1, level_item)
            self.table.setItem(row_idx, 2, msg_item)

        # Фінальне шліфування вигляду таблиці
        self.table.resizeRowsToContents()
        #self.table.resizeColumnsToContents()
        self.table.resizeColumnToContents(0)
        self.table.resizeColumnToContents(1)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Анімація появи, якщо вона у вас підключена
        fade_in_widget(self.table)

    def clear_logs(self):
        dialog = LogCleanupDialog()
        if dialog.exec():
            values = dialog.get_values()
            password = values["password"]
            if not password:
                QMessageBox.warning(self, "Помилка", "Без введення пароля очищення логів неможливе.")
                return
            log_type = values["log_type"]
            clear_all = values["clear_all_dates"]
            date_from = values.get("date_from")
            date_to = values.get("date_to")
            include_archives = values.get("include_archives", True)

            params = {
                "log_type": log_type,
                "all_dates": str(clear_all).lower(),
                "archive_before_delete": str(include_archives).lower()
            }
            if not clear_all:
                params["date_from"] = date_from
                params["date_to"] = date_to

            result = ApiClient.delete(self, f"{API_URL}/logs", params=params, data={"password": password})
            if result:
                QMessageBox.information(self, "Успіх", "Логи успішно очищено.")
                self.load_logs()

