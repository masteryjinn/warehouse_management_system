from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QAbstractItemView, QComboBox, QCheckBox, QLineEdit, QWidget, 
    QSpinBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from windows.products.product_select_dialog import ProductSelectDialog
from utils.load_styles import load_styles, load_combobox_styles

class ReasonWidget(QWidget):
    """Віджет для вибору причини: ComboBox + LineEdit (для 'Інше')."""

    # сигнал для повідомлення таблиці, що висоту треба оновити
    height_changed = pyqtSignal()

    def __init__(self, reasons, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.combo = QComboBox()
        self.combo.addItems(reasons)

        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Введіть власну причину...")
        self.line_edit.setVisible(False)

        layout.addWidget(self.combo)
        layout.addWidget(self.line_edit)

        self.combo.currentTextChanged.connect(self.toggle_line_edit)

    def toggle_line_edit(self, text):
        self.line_edit.setVisible(text == "Інше")
        self.height_changed.emit()   # 🔹 повідомляємо таблицю

    def get_reason(self):
        if self.combo.currentText() == "Інше":
            return self.line_edit.text().strip()
        return self.combo.currentText()

    def set_reason(self, reason: str):
        """Встановити причину (враховує 'Інше')."""
        if reason in [self.combo.itemText(i) for i in range(self.combo.count())]:
            self.combo.setCurrentText(reason)
        else:
            self.combo.setCurrentText("Інше")
            self.line_edit.setText(reason)
            self.line_edit.setVisible(True)
            self.height_changed.emit()

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox,
    QAbstractItemView, QComboBox, QCheckBox, QLineEdit, QWidget, 
    QSpinBox, QFrame
)

class WriteOffDialog(QDialog):
    DEFAULT_REASONS = ["Брак", "Прострочено", "Пошкоджено", "Інше"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("📉 Списання товарів")
        self.setMinimumSize(950, 650) # Трохи більше місця для ReasonWidget
        self.setStyleSheet(load_styles())
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(25, 20, 25, 20)
        main_layout.setSpacing(15)

        # 1. Заголовок
        title = QLabel("Формування акту списання")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #333;")
        main_layout.addWidget(title)

        # 2. Панель глобальних налаштувань (Групування причин)
        settings_frame = QFrame()
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #ffffff;
                border: 1px solid #e0e0e0;
                border-radius: 10px;
            }
            QLabel { border: none; font-weight: bold; }
        """)
        settings_layout = QVBoxLayout(settings_frame)

        # Рядок з чекбоксом
        check_layout = QHBoxLayout()
        self.one_reason_checkbox = QCheckBox("Застосувати одну причину для всього списку")
        self.one_reason_checkbox.setStyleSheet("border: none; font-size: 14px;")
        check_layout.addWidget(self.one_reason_checkbox)
        settings_layout.addLayout(check_layout)

        # Рядок з вибором причини (прихований за замовчуванням)
        self.global_reason_widget = QWidget()
        self.global_reason_widget.setVisible(False)
        global_reason_ui = QHBoxLayout(self.global_reason_widget)
        global_reason_ui.setContentsMargins(0, 5, 0, 0)

        global_reason_ui.addWidget(QLabel("📝 Причина:"))
        self.global_reason_combo = QComboBox()
        self.global_reason_combo.addItems(self.DEFAULT_REASONS)
        self.global_reason_combo.setMinimumWidth(200)
        self.global_reason_combo.setStyleSheet(load_combobox_styles())
        
        self.global_custom_reason = QLineEdit()
        self.global_custom_reason.setPlaceholderText("Опишіть причину детальніше...")
        self.global_custom_reason.setVisible(False)

        global_reason_ui.addWidget(self.global_reason_combo)
        global_reason_ui.addWidget(self.global_custom_reason)
        global_reason_ui.addStretch()
        
        settings_layout.addWidget(self.global_reason_widget)
        main_layout.addWidget(settings_frame)

        # 3. Кнопки керування таблицею
        btn_layout = QHBoxLayout()
        self.add_button = QPushButton("➕ Додати товар")
        self.remove_button = QPushButton("🗑️ Видалити рядок")
        btn_layout.addWidget(self.add_button)
        btn_layout.addStretch()
        btn_layout.addWidget(self.remove_button)
        main_layout.addLayout(btn_layout)

        # 4. Таблиця
        self.table = QTableWidget(0, 7)
        self.table.setHorizontalHeaderLabels([
            "Назва продукту", 
            "Доступно", 
            "Списати",
            "Причина", 
            "Секція", 
            "ID", "IDp"
        ])
        
        # Налаштування колонок
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch) # Для ReasonWidget
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        
        self.table.setColumnHidden(5, True)
        self.table.setColumnHidden(6, True)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setAlternatingRowColors(True)
        main_layout.addWidget(self.table)

        # 5. Нижні кнопки
        bottom_layout = QHBoxLayout()
        self.confirm_button = QPushButton("⚠️ Підтвердити списання")
        self.cancel_button = QPushButton("✖️ Скасувати")
        self.cancel_button.setObjectName("cancel_button")
        
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.confirm_button)
        bottom_layout.addWidget(self.cancel_button)
        main_layout.addLayout(bottom_layout)

        # Зв'язки
        self.one_reason_checkbox.stateChanged.connect(self.toggle_one_reason_mode)
        self.global_reason_combo.currentTextChanged.connect(self.update_all_reasons)
        self.global_custom_reason.textChanged.connect(self.update_all_custom_reason)
        
        self.add_button.clicked.connect(self.open_product_search)
        self.remove_button.clicked.connect(self.remove_selected_row)
        self.confirm_button.clicked.connect(self.validate_and_accept)
        self.cancel_button.clicked.connect(self.reject)

    def toggle_one_reason_mode(self, state):
        is_checked = state == Qt.CheckState.Checked.value
        self.global_reason_widget.setVisible(is_checked)
        self.global_custom_reason.setVisible(is_checked and self.global_reason_combo.currentText() == "Інше")
        
        # Логіка приховування колонки в таблиці
        self.table.setColumnHidden(3, is_checked)
        
        # Оновлюємо віджети в таблиці (як у вашому коді)
        for row in range(self.table.rowCount()):
            widget = self.table.cellWidget(row, 3)
            if isinstance(widget, ReasonWidget):
                widget.setEnabled(not is_checked)
                if is_checked:
                    val = self.global_custom_reason.text() if self.global_reason_combo.currentText() == "Інше" else self.global_reason_combo.currentText()
                    widget.set_reason(val)

    def update_all_reasons(self, text):
        show_custom = text == "Інше"
        self.global_custom_reason.setVisible(show_custom)
        if self.one_reason_checkbox.isChecked():
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, 3)
                if isinstance(widget, ReasonWidget):
                    if text != "Інше":
                        widget.set_reason(text)

    def update_all_custom_reason(self, custom_text):
        if self.one_reason_checkbox.isChecked() and self.global_reason_combo.currentText() == "Інше":
            for row in range(self.table.rowCount()):
                widget = self.table.cellWidget(row, 3)
                if isinstance(widget, ReasonWidget):
                    widget.set_reason(custom_text)

    def open_product_search(self):
        dialog = ProductSelectDialog(available_only=True)
        if dialog.exec():
            product = dialog.get_selected_product()
            if not product:
                return

            for row in range(self.table.rowCount()):
                if self.table.item(row, 6).text() == str(product["product_id"]):
                    QMessageBox.warning(self, "Помилка", "Цей продукт вже додано.")
                    return

            row = self.table.rowCount()
            self.table.insertRow(row)

            # Назва
            label = QLabel(product["name"])
            label.setWordWrap(True)   # дозволяємо перенос рядка
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setCellWidget(row, 0, label)

            # Доступно
            available_qty = product["available_quantity"]
            available_item = QTableWidgetItem(str(available_qty))
            available_item.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.table.setItem(row, 1, available_item)

            # 🔹 Кількість (через QSpinBox)
            spin = QSpinBox()
            spin.setRange(0, available_qty)  
            spin.setValue(available_qty)     
            self.table.setCellWidget(row, 2, spin)

            # Причина
            reason_widget = ReasonWidget(self.DEFAULT_REASONS)

            # якщо режим "одна причина для всіх"
            if self.one_reason_checkbox.isChecked():
                reason_widget.set_reason(
                    self.global_custom_reason.text()
                    if self.global_reason_combo.currentText() == "Інше"
                    else self.global_reason_combo.currentText()
                )
                reason_widget.combo.setEnabled(False)
                reason_widget.line_edit.setEnabled(False)

            # 🔹 прив'язуємо оновлення висоти
            reason_widget.height_changed.connect(lambda r=row: self.table.resizeRowToContents(r))

            self.table.setCellWidget(row, 3, reason_widget)


            # Секція
            section_item = QLabel(product["section_name"])
            section_item.setWordWrap(True)
            section_item.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            self.table.setCellWidget(row, 4, section_item)

            # ID секції (приховано)
            section_id_item = QTableWidgetItem(str(product["section_id"]))
            self.table.setItem(row, 5, section_id_item)

            # ID продукту (приховано)
            product_id_item = QTableWidgetItem(str(product["product_id"]))
            self.table.setItem(row, 6, product_id_item)

            self.table.resizeRowsToContents()
            
    def remove_selected_row(self):
        row = self.table.currentRow()
        if row >= 0:
            self.table.removeRow(row)
        else:
            QMessageBox.warning(self, "Увага", "Оберіть рядок для видалення.")

    def validate_and_accept(self):
        products_to_write_off = []
        for row in range(self.table.rowCount()):
            product_id = int(self.table.item(row, 6).text())
            spin = self.table.cellWidget(row, 2)
            if isinstance(spin, QSpinBox):
                qty_to_write_off = spin.value()
            else:
                try:
                    qty_to_write_off = int(self.table.item(row, 2).text())
                except Exception:
                    QMessageBox.warning(self, "Помилка", f"Невірна кількість у рядку {row+1}")
                    return


            # Причина
            widget = self.table.cellWidget(row, 3)
            if isinstance(widget, ReasonWidget):
                reason = widget.get_reason()
            else:
                reason = self.table.item(row, 3).text()

            if not reason.strip():
                QMessageBox.warning(self, "Помилка", f"Вкажіть причину у рядку {row+1}")
                return
            
            if qty_to_write_off <= 0:
                QMessageBox.warning(self, "Помилка", f"Кількість для списання має бути більше нуля у рядку {row+1}")
                return
            products_to_write_off.append({
                "product_id": product_id,
                "quantity": qty_to_write_off,
                "reason": reason,
                "section_id": int(self.table.item(row, 5).text())
            })

        if not products_to_write_off:
            QMessageBox.warning(self, "Помилка", "Список товарів порожній.")
            return

        self.products_to_write_off = products_to_write_off
        self.accept()

    def get_final_data(self):
        return getattr(self, "products_to_write_off", [])
