from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QWidget, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt, QSize
from utils.load_styles import load_dialog_styles

class NotificationItemWidget(QWidget):
    def __init__(self, title: str, message: str, note_type: str = "warning", max_length=50):
        super().__init__()

        # Замість іконки використовуємо колірну лінію збоку
        colors = {
            "error": "#e74c3c",   # Червоний
            "warning": "#f39c12", # Помаранчевий
            "default": "#3498db"  # Блакитний
        }
        self.accent_color = colors.get(note_type, colors["default"])

        # Головний лейаут
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 10, 0) # Лівий відступ 0 для лінії
        main_layout.setSpacing(15)

        # Тонка кольорова лінія-індикатор зліва
        self.status_line = QFrame()
        self.status_line.setFixedWidth(5)
        self.status_line.setStyleSheet(f"background-color: {self.accent_color}; border-radius: 2px;")
        
        # Контейнер для тексту
        text_layout = QVBoxLayout()
        text_layout.setContentsMargins(5, 10, 5, 10)
        text_layout.setSpacing(4)

        self.title_label = QLabel(title)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet(f"font-weight: bold; font-size: 11pt; color: #2c3e50; background: transparent;")

        # Обрізаємо повідомлення
        short_text = (message[:max_length] + "...") if len(message) > max_length else message
        self.message_label = QLabel(short_text)
        self.message_label.setStyleSheet("font-size: 9pt; color: #7f8c8d; background: transparent;")

        text_layout.addWidget(self.title_label)
        text_layout.addWidget(self.message_label)

        main_layout.addWidget(self.status_line) # Додаємо лінію замість іконки
        main_layout.addLayout(text_layout)
        
        self.setFixedHeight(95)
        self.set_selected(False)

    def set_selected(self, selected: bool):
        if selected:
            # При виборі лінія зливається з фоном або стає світлішою
            self.setStyleSheet(f"background-color: #3498db; border-radius: 8px;")
            self.status_line.setStyleSheet("background-color: #ecf0f1; border-radius: 1px;")
            self.title_label.setStyleSheet("color: white; font-weight: bold; font-size: 11pt; background: transparent;")
            self.message_label.setStyleSheet("color: #e0f0ff; font-size: 9pt; background: transparent;")
        else:
            self.setStyleSheet("background-color: #f5faff; border: 1px solid #d1e8ff; border-radius: 8px;")
            self.status_line.setStyleSheet(f"background-color: {self.accent_color}; border-radius: 2px;")
            self.title_label.setStyleSheet("color: #2c3e50; font-weight: bold; font-size: 11pt; background: transparent;")
            self.message_label.setStyleSheet("color: #7f8c8d; font-size: 9pt; background: transparent;")

class NotificationsDialog(QDialog):

    def __init__(self, notifications: list[dict], parent=None):

        super().__init__(parent)

        self.item_widgets = []
        self.setWindowTitle("🔔 Сповіщення")
        self.setMinimumSize(600, 720)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
        self.setStyleSheet(load_dialog_styles())

        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(15, 15, 15, 15)

        title_label = QLabel("🔔 Сповіщення")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 22px; font-weight: bold; padding-bottom: 10px; color: #2c3e50;")
        main_layout.addWidget(title_label)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)

        self.list_widget = QListWidget()
        self.list_widget.setMinimumWidth(320)
        self.list_widget.setStyleSheet("""
            QListWidget {
                background-color: transparent;
                border: none;
                outline: none;
                
            }
            QListWidget::item {
                margin-bottom: 10px;
                border: none;
                outline: none;
            }
        """)

        for note in notifications:
            item = QListWidgetItem()
            widget = NotificationItemWidget(
                title=note.get("title", "Без заголовка"),
                message=note.get("message", ""),
                note_type=note.get("type", "warning"),
                max_length=35
            )
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            item.setData(Qt.ItemDataRole.UserRole, note)
            item.setSizeHint(QSize(295, 110))
            self.item_widgets.append((item, widget))



        content_layout.addWidget(self.list_widget)



        self.details_label = QLabel()

        self.details_label.setWordWrap(True)

        self.details_label.setStyleSheet("""

            font-size: 12pt;

            color: #333333;

            padding: 12px;

            background-color: #fafafa;

            border: 1px solid #ddd;

            border-radius: 6px;
        """)
        self.details_label.setMinimumWidth(310)
        self.details_label.setMinimumHeight(200)
        content_layout.addWidget(self.details_label)

        main_layout.addLayout(content_layout)
        
        self.setLayout(main_layout)

        self.list_widget.currentItemChanged.connect(self.show_notification_details)

        if notifications:
            self.list_widget.setCurrentRow(0)
        else:
            self.details_label.setText("Сповіщень немає.")

    def show_notification_details(self, current: QListWidgetItem, previous: QListWidgetItem):
        if current is None:
            self.details_label.clear()
            return
            
        note = current.data(Qt.ItemDataRole.UserRole)
        
        
        # Формуємо красивий HTML-текст для правого поля
        full_html = f"""
            <div style='margin-bottom: 10px;'>
                <h2 style='color: #2c3e50; margin-top: 5px;'>{note.get('title')}</h2>
            </div>
            <hr style='border: 0; border-top: 1px solid #ddd;'>
            <p style='font-size: 13pt; line-height: 140%; color: #333;'>
                {note.get('details', note.get('message', ""))}
            </p>
        """
        self.details_label.setText(full_html)

        for item, widget in self.item_widgets:
            widget.set_selected(item == current)