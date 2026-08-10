import pandas as pd
import json
from PyQt6.QtWidgets import QFileDialog, QMessageBox

class ImportExportManager:
    def __init__(self, parent=None):
        self.parent = parent

    def export_data(self, data, headers):
        """
        Експорт даних у CSV, XLSX або JSON.
        Формат визначається по розширенню файлу.
        """
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self.parent,
                "Зберегти файл",
                "",
                "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
            )
            if not file_path:
                return

            if file_path.lower().endswith(".csv"):
                df = pd.DataFrame(data, columns=headers)
                df.to_csv(file_path, index=False, encoding="utf-8-sig", quotechar='"')
                file_type = "CSV"
            elif file_path.lower().endswith(".xlsx"):
                df = pd.DataFrame(data, columns=headers)
                df.to_excel(file_path, index=False, engine="openpyxl")
                file_type = "XLSX"
            elif file_path.lower().endswith(".json"):
                json_data = [dict(zip(headers, row)) if not isinstance(row, dict) else row for row in data]
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                file_type = "JSON"
            else:
                # За замовчуванням CSV
                df = pd.DataFrame(data, columns=headers)
                file_path += ".csv"
                df.to_csv(file_path, index=False, encoding="utf-8-sig", quotechar='"')
                file_type = "CSV"

            QMessageBox.information(self.parent, "Успіх", f"Дані успішно експортовано в {file_type}!")
        except Exception as e:
            QMessageBox.critical(self.parent, "Помилка експорту", str(e))

    def import_data(self):
        """
        Імпорт даних з CSV, XLSX або JSON.
        Формат визначається по розширенню файлу.
        Повертає DataFrame або None.
        """
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self.parent,
                "Відкрити файл",
                "",
                "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
            )
            if not file_path:
                return None

            if file_path.lower().endswith(".csv"):
                df = pd.read_csv(file_path, encoding="utf-8-sig", quotechar='"')
                file_type = "CSV"
            elif file_path.lower().endswith(".xlsx"):
                df = pd.read_excel(file_path, engine="openpyxl")
                file_type = "XLSX"
            elif file_path.lower().endswith(".json"):
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
                file_type = "JSON"
            else:
                QMessageBox.warning(self.parent, "Помилка", "Невідомий формат файлу.")
                return None
            print(df)
            QMessageBox.information(self.parent, "Успіх", f"Дані успішно імпортовано з {file_type}!")
            return df
        except Exception as e:
            QMessageBox.critical(self.parent, "Помилка імпорту", str(e))
            return None
