import requests
from services.signals import AppSignals
from PyQt6.QtWidgets import QMessageBox

class ErrorHandler:
    @staticmethod
    def handle_api_error(parent, exception, custom_message="Виникла помилка"):
        if isinstance(exception, requests.exceptions.ConnectionError):
            msg = "Сервер недоступний. Перевірте підключення."
        elif isinstance(exception, requests.exceptions.Timeout):
            msg = "Час очікування відповіді вичерпано."
        elif isinstance(exception, requests.exceptions.HTTPError):
            # Намагаємось дістати текст помилки з JSON-відповіді сервера
            try:
                error_data = exception.response.json()
                # Якщо detail — це рядок (як ми зробили на сервері), беремо його
                server_msg = error_data.get("detail")
                if isinstance(server_msg, list): 
                    # Для помилок валідації Pydantic (вони приходять списком)
                    server_msg = server_msg[0].get("msg")
            except Exception:
                server_msg = None

            status = exception.response.status_code
            
            if server_msg:
                # Якщо сервер надіслав зрозумілий текст — показуємо його
                msg = server_msg
            elif status == 401:
                msg = "Сесія завершена. Будь ласка, увійдіть знову."
                AppSignals.get_instance().logout_requested.emit()
            elif status == 403:
                msg = "У вас немає прав для цієї операції."
            elif status == 404:
                msg = "Ресурс не знайдено."
            else:
                msg = f"Помилка сервера: {status}"
        else:
            msg = f"{custom_message}: {str(exception)}"

        QMessageBox.critical(parent, "Помилка", msg)
        return msg