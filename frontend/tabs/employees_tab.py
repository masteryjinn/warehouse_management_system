from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                                QPushButton, QTableWidget, QTableWidgetItem,
                                QMessageBox, QLabel, QCheckBox, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
import re
import pandas as pd

from config.config import API_URL 
from user_session.current_user import CurrentUser
from services.api_client import ApiClient

from windows.employees import EmployeeFormDialog, RegisterEmployeeWindow, UpdateRoleDialog

from utils import load_styles, show_scrollable_summary, fade_in_widget
from managers.import_export_manager import ImportExportManager

class EmployeesTab(QWidget):
    def __init__(self):
        super().__init__()
        self.api_url = f"{API_URL}/employees"
        self.current_page = 1
        self.items_per_page = 15
        self.total_pages = 1

        self.init_ui()
    
    def showEvent(self, event):
        super().showEvent(event)
        self.load_employees()

    def init_ui(self):
        self.setStyleSheet(load_styles())

        layout = QVBoxLayout()
        #####self.setLayout(self.layout)

        # Поле пошуку та фільтр
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Пошук по працівниках...")
        self.btn_search = QPushButton("🔍 Пошук")
        self.btn_clear = QPushButton("♻️ Скинути")

        self.checkbox_unregistered = QCheckBox("👤 Лише незареєстровані")
        self.checkbox_unregistered.stateChanged.connect(self.perform_search)

        search_layout.addWidget(self.checkbox_unregistered)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.btn_search)
        search_layout.addWidget(self.btn_clear)

        # Таблиця співробітників
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "ПІБ працівника", "Посада", "E-mail", "Телефон", "Адреса", "Обліковий запис"
        ])
        self.table.itemSelectionChanged.connect(self.on_employee_selected)
        self.table.setAlternatingRowColors(True)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        layout.addLayout(search_layout)
        layout.addWidget(self.table)

        # Кнопки пошуку
        self.btn_search.clicked.connect(self.perform_search)
        self.btn_clear.clicked.connect(self.clear_search)

        # Кнопки CRUD
        btn_layout = QHBoxLayout()
        self.btn_add = QPushButton("➕ Додати")
        self.btn_edit = QPushButton("✏️ Редагувати")
        self.btn_register = QPushButton("🔐 Зареєструвати") 
        self.btn_delete = QPushButton("🗑️ Видалити")
        self.btn_import = QPushButton("📥 Імпорт")

        self.btn_add.clicked.connect(self.add_employee)
        self.btn_edit.clicked.connect(self.edit_employee)
        self.btn_register.clicked.connect(self.open_registration_dialog)
        self.btn_delete.clicked.connect(self.delete_employee)
        self.btn_import.clicked.connect(self.import_employee)

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_register)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addWidget(self.btn_import)
        layout.addLayout(btn_layout)

        # Пагінація
        pagination_layout = QHBoxLayout()
        self.btn_prev_page = QPushButton("⬅️ Попередня")
        self.btn_next_page = QPushButton("Наступна ➡️")
        self.page_label = QLabel(f"Сторінка {self.current_page} з {self.total_pages}")
        self.page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        pagination_layout.addWidget(self.btn_prev_page)
        pagination_layout.addWidget(self.page_label)
        pagination_layout.addWidget(self.btn_next_page)

        self.btn_prev_page.clicked.connect(self.on_prev_page)
        self.btn_next_page.clicked.connect(self.on_next_page)

        layout.addLayout(pagination_layout)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        self.setLayout(layout)        

    def perform_search(self):
        self.current_page = 1
        self.load_employees()

    def clear_search(self):
        self.search_input.clear()
        self.current_page = 1
        self.load_employees()

    def on_prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_employees()

    def on_next_page(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_employees()

    def on_employee_selected(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            return
        
        emp_id = self.table.item(current_row, 0).text()
        if not emp_id:
            return
    
        status_in_table = self.table.item(current_row, 6).text()
        is_registered = "Активний" in status_in_table

        try:
            self.btn_register.clicked.disconnect()
        except TypeError:
            pass

        if is_registered:
            self.btn_register.setText("🔄 Оновити роль")
            self.btn_register.clicked.connect(lambda: self.open_update_role_dialog(emp_id))
        else:
            self.btn_register.setText("🔐 Зареєструвати")
            self.btn_register.clicked.connect(lambda: self.open_registration_dialog(emp_id))


    def update_pagination(self, total_pages, current_page):
        self.total_pages = total_pages
        self.current_page = current_page
        
        self.page_label.setText(f"Сторінка {current_page} з {total_pages}")

        self.btn_prev_page.setEnabled(current_page > 1)
        self.btn_next_page.setEnabled(current_page < total_pages)

    def fill_table_data(self, employees):
        self.table.setRowCount(len(employees))
        for row, emp in enumerate(employees):
            # Розрахунок порядкового номера
            num = (self.current_page - 1) * self.items_per_page + row + 1
            self.table.setVerticalHeaderItem(row, QTableWidgetItem(str(num)))
            
            # Заповнення колонок
            self.table.setItem(row, 0, QTableWidgetItem(str(emp["employee_id"])))
            self.table.setItem(row, 1, QTableWidgetItem(emp["name"]))
            self.table.setItem(row, 2, QTableWidgetItem(emp["position"]))
            self.table.setItem(row, 3, QTableWidgetItem(emp.get("email", "")))
            self.table.setItem(row, 4, QTableWidgetItem(emp.get("phone", "")))
            self.table.setItem(row, 5, QTableWidgetItem(emp.get("address", "")))
            
            # Кольоровий статус з емодзі
            is_reg = emp.get("is_registered", False)
            status_text = "✅ Активний" if is_reg else "❌ Відсутній"
            state_item = QTableWidgetItem(status_text)

            # Центрування для краси
            state_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            # Твоя логіка з м'якими кольорами фону
            if is_reg:
                state_item.setBackground(QColor("#e7f5e8")) # пастельний зелений
            else:
                state_item.setBackground(QColor("#fdecea")) # пастельний червоний

            self.table.setItem(row, 6, state_item)

        self.table.setColumnHidden(0, True)
        self.table.resizeRowsToContents()
        self.table.verticalHeader().setDefaultSectionSize(35)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)


    def load_employees(self): 
        params = {
            "page": self.current_page,
            "limit": self.items_per_page,
            "search": self.search_input.text(),
            "registered_only": self.checkbox_unregistered.isChecked() 
        }

        result = ApiClient.get(self, self.api_url, params=params)
        if not result:
            return
        employees = result.get("data", [])
        total_pages = result.get("total_pages", 1)
        current_page = result.get("current_page", 1)
        self.update_pagination(total_pages, current_page)
        self.fill_table_data(employees)
        self.on_employee_selected()
        fade_in_widget(self.table)

    def import_employee(self):
        # Розширений FIELD_MAP для гнучкості імпорту працівників
        FIELD_MAP = {
            # ПІБ / Ім'я
            "ПІБ": "name", "Прізвище Ім'я": "name", "Співробітник": "name", 
            "Працівник": "name", "Name": "name", "Full Name": "name",
            # Посада
            "Посада": "position", "Роль": "position", "Position": "position", "Role": "position",
            # Адреса
            "Адреса": "address", "Місце проживання": "address", "Address": "address",
            # Телефон
            "Телефон": "phone", "Мобільний": "phone", "Контактний номер": "phone", "Phone": "phone",
            # Email
            "Email": "email", "E-mail": "email", "Пошта": "email", "Електронна пошта": "email"
        }

        manager = ImportExportManager(parent=self)
        df = manager.import_data()
        if df is None:
            return

        # Попередня перевірка: чи є у файлі обов'язкові колонки (ПІБ та Email)
        actual_columns = df.columns.tolist()
        has_name = any(FIELD_MAP.get(col) == "name" for col in actual_columns)
        has_email = any(FIELD_MAP.get(col) == "email" for col in actual_columns)

        if not has_name or not has_email:
            QMessageBox.warning(self, "Помилка структури", 
                                "У файлі не знайдено обов'язкових колонок: 'ПІБ' та 'Email'.")
            return

        data = []
        for _, row in df.iterrows():
            new_item = {"contacts": {}}

            for ukr_field, value in row.items():
                eng_field = FIELD_MAP.get(ukr_field)
                if not eng_field or pd.isna(value):
                    continue

                value = str(value).strip()
                if not value:
                    continue

                # 1. Поля профілю
                if eng_field in ["name", "position"]:
                    new_item[eng_field] = value

                # 2. Контакти (з валідацією)
                elif eng_field == "phone":
                    # Очищення від пробілів, тире, дужок
                    value = re.sub(r'[ ()\-]', '', value)

                    if not value.startswith("+"):
                        if value.startswith("380"):
                            value = "+" + value
                        elif len(value) == 10 and value.startswith("0"):
                            value = "+38" + value
                        else:
                            value = "+" + value

                    # Перевірка на цифри (мінімум 10 для валідності)
                    if len(re.sub(r'\D', '', value)) >= 10:
                        new_item["contacts"]["phone"] = value

                elif eng_field == "email":
                    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                    if re.match(email_pattern, value):
                        new_item["contacts"]["email"] = value

                elif eng_field == "address":
                    new_item["contacts"]["address"] = value

            # Жорстка перевірка: працівник без імені або пошти не імпортується
            if "name" in new_item and "email" in new_item["contacts"]:
                data.append(new_item)

        if not data:
            QMessageBox.warning(self, "Помилка імпорту", "Немає коректних даних. Переконайтеся, що Email вказано правильно.")
            return
        
        # Інформуємо про пропущені рядки (якщо такі були)
        if len(data) < len(df):
            skipped = len(df) - len(data)
            print(f"Пропущено рядків: {skipped}") # Для відладки

        result = ApiClient.post(
            self,
            f"{self.api_url}/import",
            data={"employees": data}
        )

        if result:
            message = result.get("message", "Імпорт працівників завершено успішно.")
            added = result.get("imported_names", [])
            duplicates = result.get("skipped_names", [])

            summary_text = f"{message}\n\n"
            if added:
                summary_text += "✅ Додані працівники:\n" + "\n".join(f"• {name}" for name in added) + "\n\n"
            if duplicates:
                summary_text += "⚠️ Вже існували (пропущено):\n" + "\n".join(f"• {name}" for name in duplicates)

            show_scrollable_summary(self, "Результати імпорту працівників", summary_text)
            self.load_employees()

    def add_employee(self):
        dialog = EmployeeFormDialog()
        if dialog.exec():
            data = dialog.get_data()
            if not data:
                self.show_error("Помилка: дані не були введені.")
                return
            if not all(data.values()):
                self.show_error("Помилка: всі поля повинні бути заповнені.")
                return
            result = ApiClient.post(self, self.api_url, data=data)
            if result:
                QMessageBox.information(self, "Успіх", "Працівника додано")
                self.load_employees()

    def edit_employee(self):
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть співробітника для редагування")
            return

        emp_id = int(self.table.item(current_row, 0).text())
        employee_data = {
            "name": self.table.item(current_row, 1).text(),
            "position": self.table.item(current_row, 2).text(),
            "email": self.table.item(current_row, 3).text(),
            "phone": self.table.item(current_row, 4).text(),
            "address": self.table.item(current_row, 5).text(),
        }

        dialog = EmployeeFormDialog(employee_data)
        if dialog.exec():
            updated_data = dialog.get_data()
            if not updated_data:
                self.show_error("Помилка: дані не були введені.")
                return
            if not all(updated_data.values()):
                self.show_error("Помилка: всі поля повинні бути заповнені.")
                return
            result = ApiClient.put(self, f"{self.api_url}/{emp_id}", data=updated_data)
            if result:
                QMessageBox.information(self, "Успіх", "Дані працівника оновлено")
                self.load_employees()

    def open_registration_dialog(self, emp_id):
        if emp_id is None:
            QMessageBox.warning(self, "Увага", "Оберіть співробітника для реєстрації")
            return
        dialog = RegisterEmployeeWindow()
        if dialog.exec():
            payload = dialog.get_registration_payload()
            result = ApiClient.post(self, f"{self.api_url}/register/{emp_id}", data=payload)
            if result:
                QMessageBox.information(self, "Успіх", "Користувача зареєстровано")
                self.load_employees()

    def open_update_role_dialog(self, emp_id):
        if emp_id is None:
            QMessageBox.warning(self, "Увага", "Оберіть співробітника для оновлення ролі")
            return
        employee_role_result = ApiClient.get(self, f"{self.api_url}/role/{emp_id}")
        if not employee_role_result:
            QMessageBox.warning(self, "Увага", "Не вдалося отримати роль співробітника")
            return
        
        dialog = UpdateRoleDialog(employee_role_result.get("role"))
        if dialog.exec():
            new_role = dialog.get_new_role()
            if not new_role:
                self.show_error("Помилка: роль не була вибрана.")
                return
            result = ApiClient.put(self, f"{self.api_url}/update_role/{emp_id}", data={"role": new_role})
            if result:
                QMessageBox.information(self, "Успіх", "Роль оновлено")
                self.load_employees()

    def delete_employee(self):
        current_user = CurrentUser()
        if not current_user.is_admin():
            QMessageBox.warning(self, "Увага", "У вас немає прав доступу до цієї вкладки")
            self.close()
            return
        current_row = self.table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Увага", "Оберіть співробітника")
            return

        emp_id = int(self.table.item(current_row, 0).text())
        confirm_box = QMessageBox(self)
        confirm_box.setWindowTitle("Підтвердження дії")
        confirm_box.setText("Ви впевнені, що хочете видалити співробітника?")
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

        result = ApiClient.delete(self, f"{self.api_url}/{emp_id}")
        if result:
            QMessageBox.information(self, "Успіх", "Працівника видалено")
            if self.current_page > 1 and self.table.rowCount() == 1:
                self.current_page -= 1
            self.load_employees()

    def show_error(self, message):
        QMessageBox.critical(self, "Помилка", message)
