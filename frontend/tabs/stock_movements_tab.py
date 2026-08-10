from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                                QTableWidget, QTableWidgetItem, QLabel,
                                QHeaderView, QMessageBox, QComboBox)
from PyQt6.QtCore import Qt

from services.api_client import ApiClient
from windows.stock_movements import AddIncomingDialog, RelocationDialog, WriteOffDialog, StockMovementFilterDialog

from utils import fade_in_widget, format_date
from utils.load_styles import load_styles, load_combobox_styles
from config.config import API_URL

MOVEMENT_TYPE_LABELS = {
    "in": "Надходження",
    "out": "Відвантаження",
    "transfer": "Переміщення",
    "write_off": "Списання"
}

KEYS_TRANSLATION = {
    "section_name": "Секція",
    "from_section_name": "З секції",
    "to_section_name": "До секції",
    "purchase_price": "Закупівельна ціна",
    "movement_reason": "Причина переміщення"
}

EXTRA_KEYS_CONFIG = {
    "in":       ["section_name", "purchase_price"],
    "out":      ["section_name", "movement_reason"],
    "transfer": ["from_section_name", "to_section_name", "movement_reason"],
    "write_off":["section_name", "movement_reason"]
}

class StockMovementsTab(QWidget):
    def __init__(self):
        super().__init__()
        self.current_page = 1
        self.items_per_page = 17
        self.total_pages = 1
        self.api_url= f"{API_URL}/stock_movements"
        self.movement_type_filter = "in" # За замовчуванням фільтр на "Надходження"
        self.product_id_filter = None
        self.section_id_filter = None
        self.date_from_filter = None
        self.date_to_filter = None
        self.quantity_min_filter = None
        self.quantity_max_filter = None
        self.filters = {}
        self.init_ui()

    def showEvent(self, event):
        super().showEvent(event)
        self.load_stock_movements()

    def init_ui(self):
        self.setStyleSheet(load_styles())
        layout = QVBoxLayout()
        btn_layout = QHBoxLayout()
        pagination_layout = QHBoxLayout()

        self.btn_add_incoming = QPushButton("➕ Зафіксувати надходження")
        self.btn_relocate = QPushButton("✏️ Змінити місце зберігання")
        self.btn_write_off = QPushButton("🗑️ Списати товар")
        self.btn_filter = QPushButton("🔍 Фільтрувати")
        self.btn_add_incoming.clicked.connect(self.open_add_incoming_dialog)
        self.btn_relocate.clicked.connect(self.open_relocation_dialog)
        self.btn_write_off.clicked.connect(self.open_write_off_dialog)        
        self.btn_filter.clicked.connect(self.open_filter_dialog)
        self.type_combo = QComboBox()
        #self.type_combo.addItem("Усі типи", None)
        self.type_combo.addItem("Надходження", "in")
        self.type_combo.addItem("Відвантаження", "out")
        self.type_combo.addItem("Переміщення", "transfer")
        self.type_combo.addItem("Списання", "write_off")
        self.type_combo.setStyleSheet(load_combobox_styles())
        self.type_combo.setCurrentIndex(0)  # За замовчуванням "Надходження"
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)

        btn_layout.addWidget(self.type_combo)

        btn_layout.addWidget(self.btn_add_incoming)
        btn_layout.addWidget(self.btn_relocate)
        btn_layout.addWidget(self.btn_write_off)
        btn_layout.addWidget(self.btn_filter)

        self.table = QTableWidget()
        self.table.setColumnCount(0)  # Кількість колонок буде встановлена після отримання даних
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

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

        layout.addWidget(self.table)
        layout.addLayout(btn_layout)
        layout.addLayout(pagination_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)
    
    def on_type_changed(self, index):
        selected_type = self.type_combo.currentData()  
        self.movement_type_filter = selected_type
        self.current_page = 1
        self.load_stock_movements()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_stock_movements()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_stock_movements()

    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")
        self.prev_btn.setEnabled(current_page > 1)
        self.next_btn.setEnabled(current_page < total_pages)

    def open_filter_dialog(self):
        dialog = StockMovementFilterDialog(self, self.filters)
        if dialog.exec():
            self.apply_filters(dialog)
            self.current_page = 1  # Якщо є пагінація
            self.load_stock_movements()
    
    def apply_filters(self, dialog):
        self.filters = dialog.get_filters()

        self.product_id_filter = self.filters.get("product_id")
        self.section_id_filter = self.filters.get("section_id")
        self.date_from_filter = self.filters.get("date_from")
        self.date_to_filter = self.filters.get("date_to")
        self.quantity_min_filter = self.filters.get("quantity_min")
        self.quantity_max_filter = self.filters.get("quantity_max")

    def load_stock_movements(self):
        config = {
            "in":       ["section_name", "purchase_price"],
            "out":      ["section_name", "movement_reason"],
            "transfer": ["from_section_name", "to_section_name", "movement_reason"],
            "write_off":["section_name", "movement_reason"]
        }
        
        base_labels = ["ID", "Товар", "Кількість", "Дата"]
        extra_keys = config.get(self.movement_type_filter, ["section_name", "movement_reason"])
        
        labels = base_labels + [KEYS_TRANSLATION.get(key, key) for key in extra_keys]
        self.table.setColumnCount(len(labels))
        self.table.setHorizontalHeaderLabels(labels)

        params = {
            "page": self.current_page,
            "limit": self.items_per_page,
            "movement_type": self.movement_type_filter,
            **{k: v for k, v in self.filters.items() if v not in (None, "") and k != "name"}
        }

        result = ApiClient.get(self, self.api_url, params=params)
        if not result:
            return
        
        movements = result.get("items", [])
        self.update_pagination(result.get("total_pages", 1), result.get("current_page", 1))
        
        self.table.setRowCount(len(movements))
        for row_idx, item in enumerate(movements):
            # Базові дані
            display_data = [
                str(item["movement_id"]),
                item["product_name"],
                str(item["quantity"]),
                format_date(item["movement_date"])
            ]
            # Додаткові дані згідно з конфігом
            for key in extra_keys:
                display_data.append(str(item.get(key, "")))

            for col_idx, value in enumerate(display_data):
                cell = QTableWidgetItem(value)
                cell.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row_idx, col_idx, cell)

        self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        fade_in_widget(self.table)


    def open_add_incoming_dialog(self):
        dialog = AddIncomingDialog()
        if dialog.exec():
            data = dialog.get_income_items()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, f"{self.api_url}/add_incoming", data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Інформація про надходження товару додано")
                self.type_combo.setCurrentIndex(0)  # Встановлюємо фільтр на "Надходження"
                self.movement_type_filter = "in"
                self.current_page = 1  # Якщо є пагінація
                self.load_stock_movements()

    def open_relocation_dialog(self):
        dialog = RelocationDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            result = ApiClient.post(self, f"{self.api_url}/relocate", data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Інформація про переміщення товару додано")
                self.type_combo.setCurrentIndex(2)  # Встановлюємо фільтр на "Переміщення"
                self.movement_type_filter = "transfer"
                self.current_page = 1  # Якщо є пагінація
                self.load_stock_movements()

    def open_write_off_dialog(self):
        dialog = WriteOffDialog(self)
        if dialog.exec():
            data = dialog.get_final_data()
            if not data:
                return

            # Формування запиту на сервер
            payload = {
                "movement_type": "write_off",
                "items": data
            }

            result = ApiClient.post(self, f"{self.api_url}/write_off", data=payload)
            if result:
                QMessageBox.information(self, "Успіх", "Інформація про списання товару додано")
                self.type_combo.setCurrentIndex(3)  # Встановлюємо фільтр на "Списання"
                self.movement_type_filter = "write_off"
                self.current_page = 1  # Якщо є пагінація
                self.load_stock_movements()
