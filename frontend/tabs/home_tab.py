from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QSpacerItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from utils.load_styles import load_styles

class HomeTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setStyleSheet(load_styles())

        # Основний лейаут
        home_layout = QVBoxLayout()

        # Блок для вітального повідомлення та опису програми
        message_box = QGroupBox()
        message_layout = QVBoxLayout()

        # Додамо картинку (наприклад, логотип) через QIcon
        logo_icon = QIcon("frontend/icons/main_pic.svg")  # Вкажіть шлях до вашого логотипа
        logo_label = QLabel()
        logo_label.setPixmap(logo_icon.pixmap(780, 830))  # Встановимо іконку з розмірами
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Вітальне повідомлення
        welcome_label = QLabel('Вітаємо, ви успішно увійшли в програму!')
        welcome_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        welcome_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")

        # Опис програми/компанії
        description_label = QLabel(
            'Ця програма забезпечує ефективне управління даними, включаючи працівників, клієнтів, постачальників, а також продукти, замовлення та склади. '
            'Ви отримуєте зручні інструменти для імпорту, аналізу та обробки інформації, що допомагають оптимізувати бізнес-процеси.')
        description_label.setWordWrap(True)  # Для зручності відображення тексту
        description_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description_label.setStyleSheet("font-size: 14px; color: #555;")

        # Додамо все у message_box
        message_layout.addWidget(logo_label)
        message_layout.addWidget(welcome_label)
        message_layout.addWidget(description_label)

        message_box.setLayout(message_layout)
        message_box.setStyleSheet("background-color: #e3f3f9; border-radius: 10px; padding: 20px;")

        home_layout.addWidget(message_box)

        # Завершення оформлення
        self.setLayout(home_layout)