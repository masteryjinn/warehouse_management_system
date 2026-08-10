from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame
from PyQt6.QtCore import Qt
from services.api_client import ApiClient
from config.config import API_URL

class InfoRow(QWidget):
    """Окремий рядок зі стилізацією під елемент таблиці"""
    def __init__(self, label, value, is_even=False):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 12, 20, 12)
        layout.setSpacing(10)
        
        # Фон для чергування рядків (ефект таблиці)
        bg_color = "#ffffff" if not is_even else "#f9fcff"
        self.setStyleSheet(f"background-color: {bg_color}; border: none;")
        
        # Назва поля
        self.label = QLabel(label)
        self.label.setStyleSheet("""
            color: #5d6d7e; 
            font-size: 10pt; 
            font-weight: 600; 
            text-transform: uppercase;
        """)
        self.label.setFixedWidth(150)
        
        # Значення
        self.value = QLabel(str(value) if value else "Не вказано")
        self.value.setStyleSheet("""
            color: #2c3e50; 
            font-size: 11pt; 
            font-weight: 500;
        """)
        self.value.setWordWrap(True)
        
        layout.addWidget(self.label)
        layout.addWidget(self.value)
        layout.addStretch()

class UserInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Робимо загальний фон дуже ніжно-блакитним
        self.setWindowTitle("Особистий профіль")
        self.setStyleSheet("background-color: #f0f7ff;")
        
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(35, 35, 35, 35)
        self.main_layout.setSpacing(25)

        # Заголовок з темно-синім кольором
        title_label = QLabel("Особистий профіль")
        title_label.setStyleSheet("font-size: 26px; font-weight: bold; color: #1e3a5f;")
        self.main_layout.addWidget(title_label)

        # Основна картка
        self.card = QFrame()
        self.card.setObjectName("profileCard")
        # Додаємо синю рамку та легку тінь (border-bottom)
        self.card.setStyleSheet("""
            QFrame#profileCard {
                background-color: white;
                border: 2px solid #3498db;
                border-radius: 20px;
            }
        """)
        
        self.card_layout = QVBoxLayout(self.card)
        self.card_layout.setContentsMargins(0, 0, 0, 20) # 0 зверху для кольорової плашки
        self.card_layout.setSpacing(0)

        # Верхня кольорова плашка під аватаром (оживляє картку)
        header_bg = QFrame()
        header_bg.setFixedHeight(120)
        header_bg.setStyleSheet("""
            background-color: #3498db;
            border-top-left-radius: 18px;
            border-top-right-radius: 18px;
            border: none;
        """)
        header_layout = QVBoxLayout(header_bg)
        
        avatar_label = QLabel("👤")
        avatar_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar_label.setStyleSheet("font-size: 55pt; color: white; background: transparent;")
        header_layout.addWidget(avatar_label)
        
        self.card_layout.addWidget(header_bg)

        # Контейнер для рядків (тепер з блакитними акцентами)
        self.info_container = QVBoxLayout()
        self.info_container.setContentsMargins(15, 10, 15, 10)
        self.card_layout.addLayout(self.info_container)

        self.main_layout.addWidget(self.card)
        self.main_layout.addStretch()

        self.fetch_employee_info()

    def fill_data(self, data):
        while self.info_container.count():
            child = self.info_container.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Список без смайликів
        fields = [
            ("Прізвище та ім'я", data.get("name")),
            ("Посада", data.get("position")),
            ("Електронна пошта", data.get("email")),
            ("Номер телефону", data.get("phone")),
            ("Місце проживання", data.get("address"))
        ]

        # Створюємо "табличну" частину
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            border: 1px solid #d1e8ff; 
            border-radius: 10px; 
            background-color: white;
        """)
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(0, 5, 0, 5)
        table_layout.setSpacing(0)

        for i, (label, value) in enumerate(fields):
            # Передаємо i%2 для чергування кольорів
            row = InfoRow(label, value, is_even=(i % 2 == 0))
            table_layout.addWidget(row)
            
            # Тонка лінія тільки між рядками
            if i < len(fields) - 1:
                line = QFrame()
                line.setFrameShape(QFrame.Shape.HLine)
                line.setStyleSheet("color: #eaf4ff; border: none; background-color: #eaf4ff;")
                line.setFixedHeight(1)
                table_layout.addWidget(line)

        self.info_container.addWidget(table_frame)

    def fetch_employee_info(self):
        # Твій виклик API
        result = ApiClient.get(self, f"{API_URL}/user/info")
        if result:
            self.fill_data(result)