from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QLineEdit, QLabel, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from windows.orders import OrderDialog, FilterDialog, OrderDetailsDialog, OrderCreateDialog
from services.api_client import ApiClient
from user_session.current_user import CurrentUser

from utils import load_styles, format_date, fade_in_widget
from config.config import API_URL


class OrdersTab(QWidget):
    def __init__(self):
        super().__init__()
        self.user_role = CurrentUser().get_role()  # Отримуємо роль користувача
        self.current_page = 1
        self.items_per_page = 16
        self.total_pages = 1
        self.filters=None
        self.customer_name_filter = None
        self.status_filter = None
        self.date_min = None
        self.date_max = None
        self.status_translation = {
            "draft": "Чернетка",
            "new": "Нове (Очікує)",
            "collecting": "В обробці (Збирається)",
            "review_pack": "Перевірка пакування",
            "packed": "Упаковано (Готове)",
            "shipped": "Відправлено",
            "restocking": "Очікує розпакування",
            "unpacking": "В обробці (Розпаковується)",
            "review_restock": "Перевірка повернення",
            "cancelled": "Скасовано"
        }
        self.api_url = f"{API_URL}/orders"
        self.search_query = ""
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_orders()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        layout = QVBoxLayout()

        # Пошук
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по замовленнях...")
        self.btn_search = QPushButton("🔍 Пошук")
        self.btn_clear = QPushButton("🔄 Скинути")

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_clear)

        self.btn_search.clicked.connect(self.perform_search)
        self.btn_clear.clicked.connect(self.clear_search)

        # Таблиця
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['Номер замовлення', 'Замовник', 'Дата та час створення', 'Статус замовлення'])
        layout.addLayout(search_layout)
        self.table.itemSelectionChanged.connect(self.on_order_selected)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # Кнопки
        button_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Додати")
        self.ship_btn = QPushButton("🚚 Відправити")
        self.delete_btn = QPushButton("🗑️ Видалити")
        self.filter_btn = QPushButton("🔍 Фільтр")
        self.details_btn = QPushButton("📄 Деталі замовлення")

        self.add_btn.clicked.connect(self.add_order)
        self.ship_btn.clicked.connect(self.ship_order)
        self.delete_btn.clicked.connect(self.delete_order)
        self.filter_btn.clicked.connect(self.open_filter_dialog)
        self.details_btn.clicked.connect(self.get_details_window)

        button_layout.addWidget(self.add_btn)
        button_layout.addWidget(self.ship_btn)
        button_layout.addWidget(self.delete_btn)
        button_layout.addWidget(self.filter_btn)
        button_layout.addWidget(self.details_btn)
        layout.addLayout(button_layout)

        if self.user_role == "employee":    
            self.add_btn.setEnabled(False)
            self.ship_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)

        # Пагінація
        pagination_layout = QHBoxLayout()
        self.prev_btn = QPushButton("⬅️ Попередня")
        self.next_btn = QPushButton("➡️ Наступна")
        self.page_label = QLabel(f"Сторінка {self.current_page} з {self.total_pages}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.prev_btn.clicked.connect(self.on_prev_page)
        self.next_btn.clicked.connect(self.on_next_page)

        pagination_layout.addWidget(self.prev_btn)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.next_btn)

        layout.addLayout(pagination_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)

    def next_status(self, current_status):
        status_flow = ["draft", "new", "processing", "shipped"]
        if current_status in status_flow:
            current_index = status_flow.index(current_status)
            if current_index < len(status_flow) - 1:
                return status_flow[current_index + 1]
        return current_status
    
    def nest_status_return(self, current_status):
        return "review" if current_status == "restocking" else current_status

    def perform_search(self):
        self.current_page = 1
        self.search_query = self.search_input.text()
        self.load_orders()

    def clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.search_query = ""
        self.load_orders()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_orders()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_orders()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def on_order_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        
        if not selected_rows:
            self.ship_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return

        # Беремо останній вибраний рядок для логіки кнопок Деталі/Видалити
        current_row = selected_rows[-1].row()
        status_text = self.table.item(current_row, 3).text().strip()

        # Активуємо кнопку "Відправити" тільки якщо статус "Опрацьовується (Упаковано)"
        # Це змушує менеджера діяти за правилами
        if self.user_role in ["admin", "manager"]:
            is_processing = status_text == "Упаковано (Готове)"
            self.ship_btn.setEnabled(is_processing)

        # --- Решта твоєї логіки Disconnect/Connect ---
        try: self.details_btn.clicked.disconnect()
        except: pass
        try: self.delete_btn.clicked.disconnect()
        except: pass

        if status_text == "Чернетка":
            self.details_btn.setText(" ➕ Додати товари")
            self.details_btn.clicked.connect(self.get_edit_window)
            if self.user_role == "employee":
                self.details_btn.setEnabled(False)
            self.delete_btn.setText("🗑️ Видалити")
            self.delete_btn.clicked.connect(self.delete_order)
        else:
            self.details_btn.setText("📄 Деталі замовлення")
            self.details_btn.clicked.connect(self.get_details_window)
            self.details_btn.setEnabled(True)  # Деталі доступні для всіх статусів окрім чернетки
            # Не можна видалити відправлене або скасоване
            if self.user_role in ["admin", "manager"]:
                self.delete_btn.setEnabled(status_text not in ["Відправлено", "Скасовано", "Очікує розпакування","Перевірка повернення","В обробці (Розпаковується)"])
            self.delete_btn.setText("✖️ Скасувати")
            self.delete_btn.clicked.connect(self.cancel_order)

    def open_filter_dialog(self):
        # Створення діалогу без передачі фільтрів
        dialog = FilterDialog(self, self.filters)  # Передаємо головне вікно
        if dialog.exec():
            self.apply_filters(dialog)
            self.current_page=1
            self.load_orders()

    def apply_filters(self, dialog):
        self.filters = dialog.get_filters()
        self.customer_name_filter = self.filters.get("customer_name_filter")
        self.status_filter = self.filters.get("status_filter")
        self.date_min = self.filters.get("date_min")
        self.date_max = self.filters.get("date_max")

    def fill_table_data(self, orders):
        self.table.setRowCount(len(orders))
        for row, order in enumerate(orders):
            index_number = (self.current_page - 1) * self.items_per_page + row + 1
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(index_number)))
            self.table.setItem(row, 0, QTableWidgetItem(str(order["order_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(order["customer_name"]))
            self.table.setItem(row, 2, QTableWidgetItem(format_date(order["order_date"], show_time=True)))
            translated_status = self.status_translation.get(order["status"], order["status"])
            status_item = QTableWidgetItem(translated_status)
            if order["status"] == "draft":
                # Світло-сірий: чернетка, яка ще не впливає на склад
                status_item.setBackground(QColor("#f0f0f0")) 

            elif order["status"] == "new":
                # Твій червонуватий: замовлення створено, треба звернути увагу
                status_item.setBackground(QColor("#fdecea")) 

            elif order["status"] == "processing":
                # Твій жовтий: товар у роботі (пакується)
                status_item.setBackground(QColor("#fff6d6")) 

            elif order["status"] == "shipped":
                # Твій зелений: успішно завершено
                status_item.setBackground(QColor("#e7f5e8"))

            elif order["status"] == "restocking":
                # Насичений оранжевий: УВАГА, треба фізично розібрати коробку!
                status_item.setBackground(QColor("#ffe0b2")) 

            elif order["status"] == "review":
                # Блакитний: пакувальник виконав роботу, чекає лише твого підтвердження
                status_item.setBackground(QColor("#e3f2fd"))

            elif order["status"] == "cancelled":
                # Темніший сірий або приглушений тон: замовлення закрите (невдача)
                status_item.setBackground(QColor("#cfd8dc"))

            self.table.setItem(row, 3, status_item)

        #self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_confirmation(self, message):
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText(message)
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
        return confirm_box.exec() == QMessageBox.StandardButton.Yes

    def load_orders(self):
        filters = {
            "customer_name_filter": self.customer_name_filter,
            "status_filter": self.status_filter,
            "date_min": self.date_min,
            "date_max": self.date_max,
        }

        params = {
            "page": self.current_page,
            "limit": self.items_per_page,
            "search": self.search_query,
        }

        if filters:
            params.update(filters)  # Додаємо фільтри до параметрі
        
        result = ApiClient.get(self, self.api_url, params=params)
        if result:
            orders = result.get("data", [])
            total_pages = result.get("total_pages", 1)
            current_page = result.get("current_page", 1)
            self.fill_table_data(orders)
            self.update_pagination(total_pages, current_page)
            fade_in_widget(self.table)

    def add_order(self):
        dialog = OrderDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, self.api_url, data=data)
            if result:
                #QMessageBox.information(self, "Успіх", "Замовлення успішно додано.")
                order_id = result.get("order_id")
                dialog = OrderCreateDialog(order_id)
                if dialog.exec():
                    order_items = dialog.get_order_items()
                    if not order_items:
                        QMessageBox.warning(self, "Увага", "Додайте хоча б один продукт до замовлення.")
                        return
                    payload = {"items": order_items}
                    result = ApiClient.put(self, f"{self.api_url}/{order_id}", data=payload)
                    if result:
                        QMessageBox.information(self, "Успіх", "Замовлення успішно оновлено.")
                        self.load_orders()
                else:
                    QMessageBox.warning(self, "Увага", "Замовлення було створено, але не додано жодного продукту. Ви можете відредагувати замовлення, щоб додати товари.")
                    self.load_orders()

    def ship_order(self):
        selected_indices = self.table.selectionModel().selectedRows()
        if not selected_indices:
            return

        # Збираємо ID тільки упакованих замовлень
        order_ids = []
        for index in selected_indices:
            row = index.row()
            status_text = self.table.item(row, 3).text().strip()
            if status_text == self.status_translation["packed"]:
                order_ids.append(int(self.table.item(row, 0).text()))

        if not order_ids:
            QMessageBox.warning(self, "Увага", "Немає замовлень зі статусом 'Упаковано' для відправки.")
            return

        if self.show_confirmation(f"Відправити {len(order_ids)} замовлень?"):
            # Відправляємо список ID на новий ендпоінт (bulk update)
            payload = {"order_ids": order_ids}
            result = ApiClient.put(self, f"{self.api_url}/bulk-ship", data=payload)
            
            if result:
                QMessageBox.information(self, "Успіх", f"Успішно відправлено: {len(order_ids)} замовлень.")
                self.load_orders()      

    def delete_order(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть замовлення для видалення")
            return

        order_id = int(self.table.item(current_row, 0).text())
        res = self.show_confirmation("Ви впевнені, що хочете видалити це замовлення?")
        if res:
            result = ApiClient.delete(self, f"{self.api_url}/{order_id}")
            if result:
                QMessageBox.information(self, "Успіх", "Замовлення успішно видалено.")
                if self.table.rowCount() == 1 and self.current_page > 1:
                    self.current_page -= 1
                self.load_orders()

    def cancel_order(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть замовлення для скасування")
            return

        order_id = int(self.table.item(current_row, 0).text())
        res = self.show_confirmation("Ви впевнені, що хочете скасувати це замовлення?")
        if res:
            result = ApiClient.put(self, f"{self.api_url}/{order_id}/cancel")
            if result:
                QMessageBox.information(self, "Успіх", "Замовлення успішно скасовано.")
                self.load_orders()

    def get_details_window(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть замовлення, щоб отримати детальну інформацію про нього")
            return
        order_id = int(self.table.item(current_row, 0).text())
        dialog = OrderDetailsDialog(order_id,self.api_url, is_employee=(self.user_role == "employee"))
        dialog.exec()

    def get_edit_window(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть замовлення для редагування")
            return
        order_id = int(self.table.item(current_row, 0).text())
        dialog = OrderCreateDialog(order_id)
        if dialog.exec():
            order_items = dialog.get_order_items()
            if not order_items:
                QMessageBox.warning(self, "Увага", "Додайте хоча б один продукт до замовлення.")
                return
            payload = {"items": order_items}
            result = ApiClient.put(self, f"{self.api_url}/{order_id}", data=payload)
            if result:
                QMessageBox.information(self, "Успіх", "Замовлення успішно оновлено.")
                self.load_orders()