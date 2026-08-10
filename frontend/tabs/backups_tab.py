from PyQt6.QtWidgets import (QFileDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QTableWidget, QTableWidgetItem, QMessageBox)

from services.api_client import ApiClient

from config.config import API_URL
from utils import load_styles, format_date, fade_in_widget


class BackupsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_styles())
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Заголовок
        #title = QLabel("📦 Керування бекапами бази даних")
        #title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        #title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 8px;")
        #layout.addWidget(title)

        # Верхній ряд з кнопками
        top_layout = QHBoxLayout()
        top_layout.addStretch()
        top_layout.setSpacing(10)

        self.restore_backup_btn = QPushButton("🔁 Відновити з файлу")
        self.restore_backup_btn.setStyleSheet("padding: 6px 12px;")
        self.restore_backup_btn.clicked.connect(self.restore_from_file)

        self.create_backup_btn = QPushButton("➕ Зробити бекап")
        self.create_backup_btn.setStyleSheet("padding: 6px 12px;")
        self.create_backup_btn.clicked.connect(self.create_backup)

        self.refresh_btn = QPushButton("🔄 Оновити список")
        self.refresh_btn.setStyleSheet("padding: 6px 12px;")
        self.refresh_btn.clicked.connect(self.load_backups)

        top_layout.addWidget(self.refresh_btn)
        top_layout.addWidget(self.create_backup_btn)
        top_layout.addWidget(self.restore_backup_btn)
        layout.addLayout(top_layout)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Файл", "Дата", "Розмір", "Дії"])
        self.table.setSortingEnabled(True)
        self.table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(self.table)
        self.setLayout(layout)
        self.load_backups()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_backups()

    def load_backups(self):
        result = ApiClient.get(self, f"{API_URL}/backups")
        if result:
            self.backups = result.get("backups", [])
            self.populate_table(self.backups)

    def populate_table(self, backups):
        self.table.setRowCount(len(backups)) 
        self.table.horizontalHeader().setStretchLastSection(False)
        self.table.horizontalHeader().setSectionResizeMode(0, self.table.horizontalHeader().ResizeMode.Stretch)
        self.table.setColumnWidth(1, 90)
        self.table.setColumnWidth(2, 50)
        self.table.setColumnWidth(3, 180)

        for row, backup in enumerate(backups):
            filename = backup.get("filename")
            created_at = format_date(backup.get("created_at"))
            size = backup.get("size_mb")

            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(created_at))
            self.table.setItem(row, 2, QTableWidgetItem(f"{size:.2f} MB"))

            download_btn = QPushButton("💾 Завантажити")
            restore_btn = QPushButton("🔁 Відновити")
            delete_btn = QPushButton("🗑️ Видалити")

            download_btn.setStyleSheet("padding: 4px 8px; font-size: 12px;")
            restore_btn.setStyleSheet("padding: 4px 8px; font-size: 12px;")
            delete_btn.setStyleSheet("padding: 4px 8px; font-size: 12px;")

            download_btn.clicked.connect(lambda _, fn=filename: self.download_backup(fn))
            restore_btn.clicked.connect(lambda _, fn=filename: self.restore_backup(fn))
            delete_btn.clicked.connect(lambda _, fn=filename: self.delete_backup(fn))

            btn_layout = QHBoxLayout()
            btn_layout.addWidget(download_btn)
            btn_layout.addWidget(restore_btn)
            btn_layout.addWidget(delete_btn)
            btn_layout.setContentsMargins(0, 0, 0, 0)
            btn_layout.setSpacing(5)

            btn_container = QWidget()
            btn_container.setLayout(btn_layout)

            self.table.setCellWidget(row, 3, btn_container)

        self.table.resizeRowsToContents()
        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setStretchLastSection(True)
        fade_in_widget(self.table)

    def create_backup(self):
        result = ApiClient.post(self, f"{API_URL}/backups")
        if result:
            QMessageBox.information(self, "Успіх", "Бекап створено успішно.")
            self.load_backups()

    def download_backup(self, filename):
        # Отримуємо байти файлу через ваш get_file
        content = ApiClient.get_file(self, f"{API_URL}/backups/download", params={"filename": filename})
        if content:
            save_path, _ = QFileDialog.getSaveFileName(self, "Зберегти бекап як", filename)
            if save_path:
                with open(save_path, "wb") as f:
                    f.write(content)
                QMessageBox.information(self, "Успіх", f"Файл збережено:\n{save_path}")

    def restore_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Виберіть файл бекапу", "", "Backup Files (*.sql.gz *.sql *.bak *.gz *.enc);;All Files (*)"
        )
        if not file_path:
            return   

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Підтвердження")
        msg_box.setText(f"Відновити базу даних з файлу {file_path}? Це перезапише поточну базу даних!")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        yes_button = msg_box.addButton("Так", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Ні", QMessageBox.ButtonRole.NoRole)
        
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            # Відправляємо файл через новийupload_file
            result = ApiClient.upload_file(self, f"{API_URL}/backups/restore-file", file_path)
            if result:
                QMessageBox.information(self, "Успіх", "База даних успішно відновлена з файлу.")
                self.load_backups()

    def restore_backup(self, filename):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Підтвердження")
        msg_box.setText(f"Відновити базу даних з бекапу {filename}? Це перезапише поточну базу даних!")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        yes_button = msg_box.addButton("Так", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Ні", QMessageBox.ButtonRole.NoRole)
        
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            result = ApiClient.post(self, f"{API_URL}/backups/restore", data={"filename": filename})
            if result:
                QMessageBox.information(self, "Успіх", f"База даних відновлена з {filename}.")

    def delete_backup(self, filename):
        # Отримуємо список бекапів
        if len(self.backups) <= 1:
            QMessageBox.warning(self, "Увага", "Неможливо видалити останній бекап!")
            return

        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Підтвердження")
        msg_box.setText(f"Видалити бекап {filename}?")
        msg_box.setIcon(QMessageBox.Icon.Question)
        
        yes_button = msg_box.addButton("Так", QMessageBox.ButtonRole.YesRole)
        no_button = msg_box.addButton("Ні", QMessageBox.ButtonRole.NoRole)
        
        msg_box.exec()

        if msg_box.clickedButton() == yes_button:
            result = ApiClient.delete(self, f"{API_URL}/backups", params={"filename": filename})
            if result:
                QMessageBox.information(self, "Успіх", f"Бекап {filename} видалено.")
                self.load_backups()
