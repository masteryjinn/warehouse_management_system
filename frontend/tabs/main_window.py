from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QStackedWidget,
    QListWidgetItem, QMessageBox, QMenu, QToolButton
)
from PyQt6.QtWidgets import QSizePolicy
from PyQt6.QtGui import QFont, QIcon, QMovie   
from PyQt6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QRect, QTimer
from PyQt6.QtNetwork import QNetworkAccessManager, QNetworkRequest
from PyQt6.QtCore import QUrl
from config.config import API_URL
from services.signals import AppSignals

from user_session.current_user import CurrentUser
from .home_tab import HomeTab
from windows.authorization.change_password_tab import ChangePasswordTab
from .warehouse_tab import SectionsTab
from windows.user_info.user_info_tab import UserInfoTab
from .employees_tab import EmployeesTab
from .customers_tab import CustomersTab
from .suppliers_tab import SuppliersTab
from .products_tab import ProductsTab
from .orders_tab import OrdersTab
from .stock_movements_tab import StockMovementsTab
from .report_orders_tab import ReportWindow
from .logs_tab import LogsTab
from .backups_tab import BackupsTab
from windows.notification.notifications_dialog import NotificationsDialog
from .tasks_tab import TasksTab
from .analytics_tab import AnalyticsTab

# Словник усіх можливих вкладок: (Назва, Клас, Тултіп)
ALL_TABS_CONFIG = {
    "employees": ("👥 Працівники", EmployeesTab, "Керування працівниками та їх доступом"),
    "customers": ("🧑‍💼 Клієнти", CustomersTab, "Перелік клієнтів та їх контактні дані"),
    "suppliers": ("🚚 Постачальники", SuppliersTab, "Інформація про постачальників товарів"),
    "sections": ("📦 Секції складу", SectionsTab, "Зони та секції, де зберігаються товари"),
    "products": ("📋 Перелік товарів", ProductsTab, "Усі наявні товари на складі"),
    "orders": ("🧾 Замовлення", OrdersTab, "Список замовлень і їх обробка"),
    "movements": ("🔄 Рух товару", StockMovementsTab, "Історія переміщення товарів між секціями"),
    "reports": ("📊 Звіт по замовленнях", ReportWindow, "Аналіз і статистика по замовленнях"),
    "logs": ("📜 Логи", LogsTab, "Перегляд логів системи для моніторингу дій"),
    "backups": ("📁 Бекапи", BackupsTab, "Резервні копії бази даних"),
    "tasks": ("🔧 Завдання", TasksTab, "Керування завданнями"),
    "analytics": ("📈 Аналітика", AnalyticsTab, "Аналіз даних по продажам та товарам")
}

# Карта доступу
ACCESS_MAP = {
    "admin": ["employees", "customers", "suppliers", "sections", "products", "orders", "movements", "reports", "logs", "backups", "tasks", "analytics"],
    "manager": ["customers", "suppliers", "sections", "products", "orders", "movements", "reports", "tasks", "analytics"],
    "employee": ["sections", "products", "orders", "tasks"]
}

class MainWindow(QWidget):
    def __init__(self, auth_window):
        super().__init__()
        self.auth_window = auth_window # Зберегли посилання на вікно авторизації      
        AppSignals.get_instance().logout_requested.connect(self.handle_logout)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Головне вікно")
        self.showFullScreen()

        self.network_manager = QNetworkAccessManager(self)
        self.network_manager.finished.connect(self.on_notifications_reply)
        self.notifications = None

        current_user = CurrentUser()
        user_name = current_user.get_name()
        user_role = current_user.get_role()
        self.is_temp_password = current_user.get_is_temp_password()

        # === ГОЛОВНИЙ МАКЕТ ===
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # === ЛІВА ПАНЕЛЬ (МЕНЮ) ===
        self.menu_list = QListWidget()
        self.menu_list.setMaximumWidth(270)
        self.menu_list.setStyleSheet("""
            QListWidget {
                background-color: #ecf0f1;
                border-right: 2px solid #bdc3c7;
                font-size: 18px;
                font-weight: 600;
                outline: none;
            }
            QListWidget::item {
                padding: 16px;
                margin: 5px;
                border-radius: 8px;
                color: #2c3e50;
            }
            QListWidget::item:hover {
                background-color: #d0ece7;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                border-left: 4px solid #2980b9;                     
            }
        """)
        self.menu_animation = QPropertyAnimation(self.menu_list, b"maximumWidth")
        self.menu_animation.setDuration(300)
        self.menu_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)


        # === ВМІСТ (КОНТЕНТ) ===
        self.stack = QStackedWidget()

        # Додаємо вкладки
        self.add_tab("🏠 Головна", HomeTab())
        allowed_keys = ACCESS_MAP.get(user_role, [])
        for key in allowed_keys:
            title, tab_class, _ = ALL_TABS_CONFIG[key]
            self.add_tab(title, tab_class())

        self.menu_list.setCurrentRow(0)

        # === ВЕРХНЯ ПАНЕЛЬ (ЗАГОЛОВОК + ВИХІД) ===
        header = QHBoxLayout()

        # Кнопка для приховування меню
        self.toggle_menu_button = QToolButton(self)
        self.toggle_menu_button.setIcon(QIcon("frontend/icons/menu_close.png"))
        self.toggle_menu_button.setIconSize(QSize(30, 30))
        self.toggle_menu_button.setStyleSheet("background-color: transparent; border: none;")
        self.toggle_menu_button.clicked.connect(self.toggle_menu)

        # Назва програми
        app_name_label = QLabel("Програма для управління складом")
        app_name_label.setFont(QFont("Arial", 20, QFont.Weight.Bold))
        app_name_label.setStyleSheet("""
            color: white;
            padding-left: 10px;
        """)

        self.notification_button_container = QWidget()
        self.notification_button_container.setFixedSize(80, 80)
        self.notification_button_container.setStyleSheet("background-color: transparent;")    

        self.notifications_btn = QToolButton(self.notification_button_container)
        self.notifications_btn.setIcon(QIcon("frontend/icons/bell.png"))
        self.notifications_btn.setIconSize(QSize(64, 64))  # збільшуємо іконку
        self.notifications_btn.setToolTip("Сповіщення")
        self.notifications_btn.setStyleSheet("background-color: transparent; border: none;")
        self.notifications_btn.setGeometry(5, 5, 70, 70)  
        self.notifications_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.notifications_btn.clicked.connect(lambda: self.fetch_notifications_from_server(open_after=True))

        self.red_dot = QLabel(self.notification_button_container)
        self.red_dot.setFixedSize(12, 12)  # можна 12x12 або збільшити
        self.red_dot.setStyleSheet("""
            QLabel {
                background-color: red;
                border-radius: 6px;
                border: 2px solid white;
            }
        """)
        # Розміщуємо крапочку зверху праворуч від кнопки
        self.red_dot.move(46, 18) # позиція близько до правого верхнього кута кнопки
        self.red_dot.raise_()     # Піднімаємо над кнопкою, щоб була видима
        self.red_dot.hide()

        # Поточна позиція і розмір крапочки
        x, y = 46, 18
        size_small = 12
        size_big = 18

        self.red_dot.setGeometry(x, y, size_small, size_small)

        self.red_dot_pulse_animation = QPropertyAnimation(self.red_dot, b"geometry")
        self.red_dot_pulse_animation.setDuration(800)  # швидкість анімації в мс
        self.red_dot_pulse_animation.setLoopCount(-1)  # безкінечний цикл
        self.red_dot_pulse_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Встановлюємо ключові кадри анімації:
        self.red_dot_pulse_animation.setKeyValueAt(0, QRect(x, y, size_small, size_small))
        self.red_dot_pulse_animation.setKeyValueAt(0.5, QRect(x - 3, y - 3, size_big, size_big))  # трохи збільшуємо і зсуваємо вгору і вліво, щоб центр залишився близько того самого
        self.red_dot_pulse_animation.setKeyValueAt(1, QRect(x, y, size_small, size_small))

        # Кнопка користувача з випадаючим меню
        self.user_button = QToolButton(self)
        self.user_button.setText(f"{user_name}")
        self.user_button.setIcon(QIcon("frontend/icons/user_icon.png"))
        self.user_button.setStyleSheet("""
            QToolButton {
                color: white;
                background-color: #3498db;
                padding: 8px 14px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 18px;
            }
            QToolButton:hover {
                background-color: #1f669d;
                
            }
        """)
        self.user_button.setFont(QFont("Arial", 14))
        self.user_button.setIconSize(QSize(40, 40))
        self.user_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.user_button.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self.user_button.clicked.connect(self.show_user_menu)

        header.addWidget(self.toggle_menu_button)
        header.addWidget(app_name_label)
        header.addWidget(self.notification_button_container)
        header.addWidget(self.user_button)

        top_panel = QWidget()
        top_panel.setLayout(header)
        top_panel.setStyleSheet("""background-color: #3498db; padding: 10px;""")

        # === ОСНОВНИЙ КОНТЕЙНЕР ===
        content_layout = QVBoxLayout()
        content_layout.addWidget(top_panel)
        content_layout.addWidget(self.stack)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        content_layout.setStretch(0, 1)
        content_layout.setStretch(1, 10)

        stack_container = QWidget()
        stack_container.setLayout(content_layout)
        stack_container.setStyleSheet("background-color: #fdfefe;")

        main_layout.addWidget(self.menu_list)
        main_layout.addWidget(stack_container)

        self.setLayout(main_layout)

        # === Запуск таймера для періодичного запиту сповіщень ===
        self.notification_timer = QTimer(self)
        self.notification_timer.timeout.connect(self.fetch_notifications_from_server)
        self.notification_timer.start(5 * 60 * 1000)  # кожні 5 хвилин

        # Отримуємо сповіщення одразу при запуску
        self.fetch_notifications_from_server()

        # Aдаптивне поведінка для вмісту
        self.stack.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.menu_list.currentRowChanged.connect(self.stack.setCurrentIndex)

        if self.is_temp_password:
            self.change_password_tab = ChangePasswordTab(is_temp_password=True)
            self.change_password_tab.setWindowModality(Qt.WindowModality.ApplicationModal)
            self.change_password_tab.show()

    def fetch_notifications_from_server(self, open_after=False):
        """Надсилає GET-запит на сервер для отримання сповіщень"""

        self._open_after = open_after  # Запам'ятовуємо, чи відкривати діалог після завантаження

        request = QNetworkRequest(QUrl(f"{API_URL}/notifications"))
        token = CurrentUser().get_token()
        request.setRawHeader(b"Authorization", f"Bearer {token}".encode())

        self.network_manager.get(request)  # Асинхронний запит

    def on_notifications_reply(self, reply):

        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        if status_code != 200:
            error_message = reply.errorString()
            print(f"[Сповіщення] Помилка HTTP {status_code}: {error_message}")
            self.update_notification_indicator(False)
            reply.deleteLater()
            return

        try:
            data_bytes = reply.readAll()
            data_str = bytes(data_bytes).decode("utf-8")

            import json
            data = json.loads(data_str)
            self.notifications = data.get("notifications", [])

            self.update_notification_indicator(bool(self.notifications))

            if getattr(self, "_open_after", False):
                if self.notifications:
                    self.open_notifications_dialog()

        except Exception as e:
            print(f"[Сповіщення] Помилка обробки JSON: {str(e)}")
            self.update_notification_indicator(False)

        reply.deleteLater()

    def update_notification_indicator(self, has_notifications: bool):
        if has_notifications:
            self.red_dot.show()
            self.red_dot_pulse_animation.start()
        else:
            self.red_dot_pulse_animation.stop()
            self.red_dot.hide()

    def open_notifications_dialog(self):
        """Відкриває діалогове вікно зі сповіщеннями"""
        dialog = NotificationsDialog(self.notifications, self)
        dialog.exec()

    def toggle_menu(self):
        """Плавно приховує або показує меню"""
        current_width = self.menu_list.maximumWidth()
        if current_width > 0:
            target_width = 0
            self.toggle_menu_button.setIcon(QIcon("frontend/icons/menu_open.png"))
        else:
            target_width = 250
            self.toggle_menu_button.setIcon(QIcon("frontend/icons/menu_close.png"))

        self.menu_animation.stop()
        self.menu_animation.setStartValue(current_width)
        self.menu_animation.setEndValue(target_width)
        self.menu_animation.start()

    def add_tab(self, name, widget):
        item = QListWidgetItem(name)
        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Шукаємо тултіп у конфігурації за назвою вкладки
        # Якщо не знайшли - використовуємо назву як тултіп за замовчуванням
        tooltip_text = name
        for key, config in ALL_TABS_CONFIG.items():
            if config[0] == name:
                tooltip_text = config[2]
                break
                
        item.setToolTip(tooltip_text)
        self.menu_list.addItem(item)
        self.stack.addWidget(widget)

    def logout(self):
        """Діалогове вікно для виходу з акаунту або програми з повідомленням серверу"""
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Вихід")
        msg_box.setText("Ви хочете вийти з акаунту чи закрити програму?")
        
        # Стилі залишаємо як раніше
        msg_box.setStyleSheet("""
                QMessageBox {
                    background-color: #ffffff;
                }
                QLabel {
                    color: #2c3e50;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton {
                    background-color: #ecf0f1;
                    color: #2c3e50;
                    border: 1px solid #bdc3c7;
                    padding: 6px 12px;
                    font-size: 14px;
                    font-weight: bold;
                    min-width: 80px;
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #d0d3d4;
                }
            """)

        logout_btn = msg_box.addButton("Вийти з акаунту", QMessageBox.ButtonRole.YesRole)
        exit_btn = msg_box.addButton("Вийти з програми", QMessageBox.ButtonRole.NoRole)
        cancel_btn = msg_box.addButton("Скасувати", QMessageBox.ButtonRole.RejectRole)

        msg_box.exec()
        clicked = msg_box.clickedButton()

        if clicked == cancel_btn:
            return

        current_user = CurrentUser()
        
        # Створюємо запит
        request = QNetworkRequest(QUrl(f"{API_URL}/logout"))
        request.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, "application/json")
        
        token = current_user.get_token()
        request.setRawHeader(b"Authorization", f"Bearer {token}".encode())

        # Відправляємо POST запит (пустий body, якщо сервер не чекає даних)
        reply = self.network_manager.post(request, b"")
        
        # Оскільки програма має закритися ПІСЛЯ відповіді, 
        # ми можемо підключитися до завершення саме цього запиту
        reply.finished.connect(lambda: self.finish_logout(reply, clicked, logout_btn))

    def finish_logout(self, reply, clicked, logout_btn):
        status_code = reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute)
        
        if status_code == 200:
            CurrentUser().clear_user_data()
            self.close()
            if clicked == logout_btn:
                if self.auth_window:
                    self.auth_window.show()
            else:
                exit()
        else:
            QMessageBox.warning(self, "Помилка", f"Сервер повернув помилку: {status_code}")
        
        reply.deleteLater()

    def show_user_menu(self):
        """Відкриває випадаюче меню користувача"""
        user_menu = QMenu(self)

        personal_info_action = user_menu.addAction("Особиста інформація")
        change_password_action = user_menu.addAction("Змінити пароль")
        logout_action = user_menu.addAction("Вийти")

        user_menu.setStyleSheet("""
            QMenu {
                background-color: #3498db;
                border: 1px solid #2980b9;
                padding: 5px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QMenu::item {
                padding: 6px 14px;
                border-radius: 4px;
                background-color: transparent;
                color: white;
            }
            QMenu::item:selected {
                background-color: #1f669d;
                color: white;
            }
        """)

        personal_info_action.triggered.connect(self.open_personal_info)
        change_password_action.triggered.connect(self.open_change_password_tab)
        logout_action.triggered.connect(self.logout)

        user_menu.exec(self.user_button.mapToGlobal(self.user_button.rect().bottomLeft()))

    def open_personal_info(self):
        """Відкриває вікно з особистою інформацією"""
        self.personal_info_window = UserInfoTab()  # Відкриваємо вкладку з особистою інформацією
        self.personal_info_window.show()

    def open_change_password_tab(self):
        """Відкриває вкладку з налаштуваннями (змінити пароль)"""
        self.change_password_tab = ChangePasswordTab()  # Відкриваємо вкладку з налаштуваннями
        self.change_password_tab.show()

    def handle_logout(self):
        self.close()
        if self.auth_window:
            self.auth_window.show()