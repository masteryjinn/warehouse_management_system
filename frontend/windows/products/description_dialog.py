from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTextEdit, QPushButton, 
    QHBoxLayout, QLabel, QFrame
)
from PyQt6.QtCore import Qt
from utils.load_styles import load_dialog_styles

class DescriptionDialog(QDialog):
    def __init__(self, initial_text=""):
        super().__init__()
        self.setWindowTitle("📝 Редагування опису")
        self.setMinimumSize(650, 450)
        self.setStyleSheet(load_dialog_styles())

        self.init_ui(initial_text)

    def init_ui(self, initial_text):
        # Головний лейаут з відступами
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(12)

        # 1. Заголовок та підказка
        header_layout = QHBoxLayout()
        title_label = QLabel("Детальний опис товару")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50;")
        
        info_label = QLabel("дозволено HTML") # Якщо плануєш рендерити як rich text
        info_label.setStyleSheet("color: #7f8c8d; font-size: 12px; font-style: italic;")
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(info_label)
        main_layout.addLayout(header_layout)

        # 2. Поле вводу
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Опишіть ключові характеристики, переваги або особливості зберігання...")
        self.text_edit.setPlainText(initial_text)
        
        # Виносимо стилі в окрему змінну для чистоти, або використовуємо зовнішні
        self.text_edit.setStyleSheet("""
            QTextEdit {
                padding: 15px;
                border: 2px solid #e0e4e8;
                border-radius: 10px;
                font-size: 14px;
                line-height: 1.5;
                selection-background-color: #3498db;
                background-color: #ffffff;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        main_layout.addWidget(self.text_edit)

        # 3. Додаткова панель (Лічильник або кнопка очищення)
        footer_info = QHBoxLayout()
        self.char_count_label = QLabel(f"Символів: {len(initial_text)}")
        self.char_count_label.setStyleSheet("color: #95a5a6; font-size: 12px;")
        
        clear_btn = QPushButton("🧹 Очистити")
        clear_btn.setFlat(True)
        clear_btn.clicked.connect(lambda: self.text_edit.clear())
        
        footer_info.addWidget(self.char_count_label)
        footer_info.addStretch()
        footer_info.addWidget(clear_btn)
        main_layout.addLayout(footer_info)

        # 4. Нижні кнопки
        buttons = QHBoxLayout()
        buttons.setSpacing(15)

        self.save_btn = QPushButton("✅ Зберегти опис")
        self.save_btn.setMinimumHeight(40)

        self.cancel_btn = QPushButton("✖️ Скасувати")
        self.cancel_btn.setObjectName("cancel_button")
        self.cancel_btn.setMinimumHeight(40)
        
        buttons.addStretch()
        buttons.addWidget(self.save_btn)
        buttons.addWidget(self.cancel_btn)
        main_layout.addLayout(buttons)

        # Події
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.text_edit.textChanged.connect(self.update_char_count)

    def update_char_count(self):
        count = len(self.text_edit.toPlainText())
        self.char_count_label.setText(f"Символів: {count}")

    def get_description(self):
        return self.text_edit.toPlainText().strip()