import requests
from user_session.current_user import CurrentUser
from services.error_handler import ErrorHandler

class ApiClient:
    """Клас для централізованого виконання HTTP-запитів"""
    
    @staticmethod
    def _get_headers():
        return CurrentUser().get_auth_header()

    @classmethod
    def get(cls, parent, url, params=None):
        headers = cls._get_headers()
        if not headers: return None
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None

    @classmethod
    def post(cls, parent, url, data=None):
        headers = cls._get_headers()
        if not headers: return None
        
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            if response.status_code == 422:
                # Обробка помилки валідації з детальним повідомленням
                error_detail = response.json().get('detail', 'Невідома помилка валідації')
                print(f"Помилка валідації: {error_detail}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None
        
    @classmethod
    def delete(cls, parent, url, params=None, data=None):
        headers = cls._get_headers()
        if not headers: return None
        
        try:
            response = requests.delete(url, headers=headers, params=params, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None
    
    @classmethod
    def put(cls, parent, url, data=None):
        headers = cls._get_headers()
        if not headers: return None
        
        try:
            print(f"DEBUG: PUT {url} with data: {data}")
            response = requests.put(url, headers=headers, json=data, timeout=10)
            print(f"DEBUG: Response status: {response.status_code}, body: {response.text}")
            response.raise_for_status()
            return response.json()
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None
        
    @classmethod
    def patch(cls, parent, url, data=None):
        headers = cls._get_headers()
        if not headers: return None
        
        try:
            response = requests.patch(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None

    @classmethod
    def get_file(cls, parent, url, params=None):
        headers = cls._get_headers()
        if not headers: return None
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30, stream=True)
            response.raise_for_status()
            return response.content
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None
        
    @classmethod
    def upload_file(cls, parent, url, file_path, data=None):
        """Надсилання файлу на сервер (Upload)"""
        headers = cls._get_headers()
        if not headers: 
            return None

        # Зверніть увагу: при відправці multipart/form-data requests САМ формує 
        # Content-Type з boundary, тому якщо у ваших headers є "Content-Type": "application/json",
        # його краще видалити для цього конкретного запиту:
        upload_headers = {k: v for k, v in headers.items() if k.lower() != 'content-type'}

        try:
            # Відкриваємо файл у бінарному режимі
            with open(file_path, "rb") as f:
                filename = file_path.split("/")[-1].split("\\")[-1]  # Отримуємо назву файлу
                files = {"file": (filename, f, "application/octet-stream")}
                
                response = requests.post(
                    url, 
                    headers=upload_headers, 
                    files=files, 
                    data=data, 
                    timeout=60  # Збільшений таймаут, бо файл може завантажуватися довше
                )
                response.raise_for_status()
                return response.json() if response.text else True
        except Exception as e:
            ErrorHandler.handle_api_error(parent, e)
            return None