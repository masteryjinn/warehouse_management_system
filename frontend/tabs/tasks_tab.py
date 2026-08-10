from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QMessageBox, QLabel, QDialog,
                                QHeaderView, QComboBox)
from PyQt6.QtCore import Qt

from windows.tasks import CreateTaskDialog, TaskFilterDialog
from services.api_client import ApiClient
from user_session.current_user import CurrentUser# зручно для отримання ролі та ID(!!!!) поточного користувача

from config.config import API_URL
from utils import load_styles, fade_in_widget, format_date

# Емоджі може постирай і залиш текст

STATUS_TRANSLATIONS = {
    "new": "Нове",
    "in_progress": "У процесі",
    "under_review": "На перевірці",
    "completed": "Завершено",
    "cancelled": "Скасовано"
}

PRIORITY_TRANSLATIONS = {
    "low": "Низький",
    "medium": "Середній",
    "high": "Високий"
}

class TasksTab(QWidget):
    def __init__(self):
        super().__init__()
        self.api_url = f"{API_URL}/tasks"
        self.last_filters = {  
            "search": None,
            "status": None,
            "priority": None,
            "employee_id": None,
            "employee_name": None,
            "start_date": None,
            "end_date": None
        }
        # Параметри фільтрів і пагінації
        self.current_page = 1
        self.page_size = 12
        self.total_pages = 1
        self.status_tab_filter = None
        self.search_query = ""

        self.init_ui()

    def init_ui(self):
        self.setStyleSheet(load_styles())
        layout = QVBoxLayout(self)
        
        # Верхня панель з фільтрами та пошуком
        filter_layout = QHBoxLayout()

        self.status_combo = QComboBox()
        self.status_combo.addItem("Усі", None)
        self.status_combo.addItem("Активні", "active")
        self.status_combo.addItem("Архівні", "archived")
        self.status_combo.currentIndexChanged.connect(self.apply_filters)
        filter_layout.addWidget(QLabel("Статус:"))
        filter_layout.addWidget(self.status_combo)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по назві завдання...")
        filter_layout.addWidget(self.search_input)

        self.search_btn = QPushButton("🔍 Пошук")
        self.search_btn.clicked.connect(self.apply_filters)
        filter_layout.addWidget(self.search_btn)

        self.reset_btn = QPushButton("🔄 Скинути")
        self.reset_btn.clicked.connect(self.reset_filters)
        filter_layout.addWidget(self.reset_btn)

        layout.addLayout(filter_layout)

        # Кнопки створення і оновлення
        btn_layout = QHBoxLayout()
        self.create_task_btn = QPushButton("➕ Створити завдання")
        self.create_task_btn.clicked.connect(self.open_create_task_dialog)
        btn_layout.addWidget(self.create_task_btn)

        self.refresh_btn = QPushButton("🔃 Оновити")
        self.refresh_btn.clicked.connect(self.load_tasks)
        btn_layout.addWidget(self.refresh_btn)
        btn_layout.addStretch()

        self.filter_btn = QPushButton("⚙️ Фільтр")
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        btn_layout.addWidget(self.filter_btn)

        layout.addLayout(btn_layout)

        # Таблиця завдань
        self.table = QTableWidget()
        self.table.setColumnCount(12)
        self.table.setHorizontalHeaderLabels([
            "ID", "Назва", "Опис", "Пріоритет", "Статус", "Створив", "Дедлайн",
            "Виконавці", "Дія", "Подати на перевірку", "Адмін. дії", "Опис (прих.)"
        ])
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.cellClicked.connect(self.handle_table_click)
        self.table.setSortingEnabled(False)
        self.table.setColumnHidden(11, True)  # Прихований стовпець з повним описом
        layout.addWidget(self.table)

        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("Попередня")
        self.next_btn = QPushButton("Наступна")
        self.page_label = QLabel(f"Сторінка {self.current_page} з {self.total_pages}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn.clicked.connect(self.prev_page)
        self.next_btn.clicked.connect(self.next_page)

        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)

        layout.addLayout(pagination_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

        self.update_ui_by_role()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_tasks()
    
    def open_filter_dialog(self):
        dialog = TaskFilterDialog(self, last_filters=self.last_filters)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            filters = dialog.get_filters()
            self.last_filters = filters 
            self.current_page = 1
            self.load_tasks()

    def apply_filters(self):
        self.status_tab_filter = self.status_combo.currentData()
        self.search_query = self.search_input.text().strip()
        self.current_page = 1
        self.load_tasks()

    def reset_filters(self):
        self.status_combo.setCurrentIndex(0)
        self.search_input.clear()
        self.status_tab_filter = None
        self.search_query = ""
        self.current_page = 1
        self.load_tasks()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_tasks()

    def next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_tasks()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")

        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def load_tasks(self):
        params = {
            "page": self.current_page,
            "page_size": self.page_size
        }
        if self.status_tab_filter:
            params["status_tab"] = self.status_tab_filter
        if self.search_query:
            params["search"] = self.search_query
        if self.last_filters.get("status"):
            params["status"] = self.last_filters["status"]
        if self.last_filters.get("priority"):
            params["priority"] = self.last_filters["priority"]
        if self.last_filters.get("employee_id"):
            params["employee_id"] = self.last_filters["employee_id"]
        if self.last_filters.get("start_date"):
            params["start_date"] = self.last_filters["start_date"]
        if self.last_filters.get("end_date"):
            params["end_date"] = self.last_filters["end_date"]
        result = ApiClient.get(self, self.api_url, params=params)
        if result:
            self.tasks = result.get("tasks", [])
            total_pages = result.get("total_pages", 1)
            current_page = result.get("current_page", 1)
            self.update_pagination(total_pages, current_page)
            self.populate_table()
            self.update_ui_by_status(self.status_tab_filter)    

    def handle_table_click(self, row, column):
        if column == 2:
            item = self.table.item(row, 11) # Опис завдання
            description = item.text() if item else "Немає опису"
            self.show_description_popup(description)
        
    def show_description_popup(self, description: str):
        QMessageBox.information(self, "Опис завдання", description)

    def update_ui_by_role(self):
        self.current_user = CurrentUser()
        self.create_task_btn.setVisible(self.current_user.is_admin() or self.current_user.is_manager())
        if self.current_user.is_employee():
            self.table.setColumnHidden(10, True)
        elif self.current_user.is_manager() or self.current_user.is_admin():
            self.table.setColumnHidden(8, True)
            self.table.setColumnHidden(9, True)

    def update_ui_by_status(self, status):
        if status == "archived":
            self.table.setColumnHidden(10, True)

    def populate_table(self):
        self.table.setRowCount(len(self.tasks))
        user_id = self.current_user.get_user_id()
        is_emp = self.current_user.is_employee()
        is_adm = self.current_user.is_admin() or self.current_user.is_manager()

        for row, task in enumerate(self.tasks):
            t_id = task.get("task_id")
            status = task.get("status")
            assignees = task.get("assignees", [])
            is_assigned = any(a["user_id"] == user_id for a in assignees)

            # --- 1. Текстові дані ---
            self._set_row_text_items(row, task)

            # --- 2. Логіка для Співробітника (Стовпці 8, 9) ---
            if is_emp:
                self._setup_employee_actions(row, t_id, status, task, is_assigned)
            else:
                self.table.setCellWidget(row, 8, QLabel("-"))
                self.table.setCellWidget(row, 9, QLabel("-"))

            # --- 3. Логіка для Адміна/Менеджера (Стовпець 10) ---
            if is_adm:
                self._setup_admin_actions(row, t_id, status)

        self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        fade_in_widget(self.table)

    def _set_row_text_items(self, row, task):
        self.table.setItem(row, 0, QTableWidgetItem(str(task.get("task_id"))))
        self.table.setItem(row, 1, QTableWidgetItem(task.get("title", "")))
        self.table.setItem(row, 2, QTableWidgetItem("ℹ️"))
        priority_ukr = PRIORITY_TRANSLATIONS.get(task.get("priority"), task.get("priority"))
        self.table.setItem(row, 3, QTableWidgetItem(priority_ukr))
        status_ukr = STATUS_TRANSLATIONS.get(task.get("status"), task.get("status"))
        self.table.setItem(row, 4, QTableWidgetItem(status_ukr))
        self.table.setItem(row, 5, QTableWidgetItem(task.get("creator_name", "")))
        self.table.setItem(row, 6, QTableWidgetItem(format_date(task.get("deadline"), show_time=True)))
        assignees_names = ", ".join([a["name"] for a in task.get("assignees", [])])
        self.table.setItem(row, 7, QTableWidgetItem(assignees_names))
        self.table.setItem(row, 11, QTableWidgetItem(task.get("description", "")))  # Прихований опис

    def _create_btn(self, text, callback, enabled=True, style=None):
        """Універсальний помічник для створення кнопок"""
        btn = QPushButton(text)
        btn.setEnabled(enabled)
        if callback and enabled:
            btn.clicked.connect(callback)
        return btn

    def _setup_employee_actions(self, row, tid, status, task, is_assigned):
        if status in ["completed", "cancelled"]:
            self.table.setCellWidget(row, 8, QLabel("-"))
            self.table.setCellWidget(row, 9, QLabel("-"))
            return
        else:    
            # Кнопка взяття/відмови
            if not is_assigned:
                can_take = task.get("assigned_count", 0) < task.get("max_assignees", 1)
                txt = "Взяти\nзавдання" if can_take else "Ліміт\nзаповнено"
                btn = self._create_btn(txt, lambda: self.take_task(tid), enabled=can_take)
            else:
                btn = self._create_btn("Ви вже\nвиконуєте", None, enabled=False)
            self.table.setCellWidget(row, 8, btn)

            # Кнопка подачі на перевірку
            can_submit = is_assigned and status == "in_progress"
            submit_btn = self._create_btn("Подати на\nперевірку", 
                                        lambda: self.change_status(tid, "under_review"), 
                                        enabled=can_submit)
            self.table.setCellWidget(row, 9, submit_btn)

    def _setup_admin_actions(self, row, tid, status):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(2)

        if status == "under_review":
            layout.addWidget(self._create_btn("✅ Підтвердити", lambda: self.change_status(tid, "completed")))
            layout.addWidget(self._create_btn("🔄 Повернути", lambda: self.change_status(tid, "in_progress")))
        
        if status in ["in_progress", "under_review"]:
            layout.addWidget(self._create_btn("❌ Скасувати", lambda: self.change_status(tid, "cancelled")))
        
        if status == "new":
            layout.addWidget(self._create_btn("🗑 Видалити", lambda: self.delete_task(tid)))

        self.table.setCellWidget(row, 10, container)

    def open_create_task_dialog(self):
        dialog = CreateTaskDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            data = dialog.get_task_data()
            if not data["title"]:
                QMessageBox.warning(self, "Помилка", "Назва завдання не може бути порожньою")
                return
            self.create_task(data)

    def create_task(self, task_data):
        result = ApiClient.post(self, self.api_url, data=task_data)
        if result:
            QMessageBox.information(self, "Успіх", "Завдання створено успішно")
            self.load_tasks()

    def take_task(self, task_id):
        result = ApiClient.post(self, f"{self.api_url}/{task_id}/assign")
        if result:
            QMessageBox.information(self, "Успіх", "Ви успішно взяли завдання")
            self.load_tasks()

    def change_status(self, task_id, new_status, reload_after=True):
        result = ApiClient.patch(self, f"{self.api_url}/{task_id}/status", data={"status": new_status})
        if result:
            QMessageBox.information(self, "Успіх", f"Статус завдання оновлено на '{STATUS_TRANSLATIONS.get(new_status, new_status)}'")
            if reload_after:
                self.load_tasks()

    def delete_task(self, task_id):
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText("Ви впевнені, що хочете видалити це завдання?")
        confirm_box.setIcon(QMessageBox.Icon.Warning)
        confirm_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        confirm_box.setDefaultButton(QMessageBox.StandardButton.No)
        confirm_box.button(QMessageBox.StandardButton.Yes).setText("Так")
        confirm_box.button(QMessageBox.StandardButton.No).setText("Ні")

        # Додатковий стиль (необов’язково)
        confirm_box.setStyleSheet("""
            QMessageBox {
                color: #ecf0f1;
                font-size: 14px;
            }
            QPushButton {
                min-width: 80px;
                font-size: 13px;
                padding: 5px 10px;
            }
        """)

        # Показ і перевірка відповіді
        confirm = confirm_box.exec()
        if confirm != QMessageBox.StandardButton.Yes:
            return

        result = ApiClient.delete(self, f"{self.api_url}/{task_id}")
        if result:
            QMessageBox.information(self, "Успіх", "Завдання успішно видалено")
            if self.current_page > 1 and self.table.rowCount() == 1:
                self.current_page -= 1
            self.load_tasks()
