from services.signals import AppSignals    

class CurrentUser:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CurrentUser, cls).__new__(cls)
            cls._instance.user_id = None
            cls._instance.name = None
            cls._instance.role = None
            cls._instance.token = None
            cls._instance.is_temp_password = None
        return cls._instance
    
    def get_auth_header(self):
        """Повертає заголовок авторизації для запитів
         у випадку відсутності токена ініціює вихід користувача"""
        if not self.token:
            print("Системна помилка: Спроба запиту без токена.")
            AppSignals.get_instance().logout_requested.emit()
            return None
            
        return {"Authorization": f"Bearer {self.token}"}

    def set_user_data(self, user_id, name, role, token, is_temp_password=None):
        """Встановлюємо дані користувача"""
        self.user_id = user_id
        self.name = name
        self.role=role
        self.token = token
        self.is_temp_password = is_temp_password
    
    def get_user_data(self):
        return {
            'user_id': self.user_id,
            'name': self.name,
            'role': self.role,
            'token': self.token, 
            'is_temp_password': self.is_temp_password
        }
    
    def get_user_id(self):
        """Отримуємо ID користувача"""
        return self.user_id

    def get_role(self): 
        """Отримуємо роль користувача"""
        return self.role
    
    def get_name(self):
        """Отримуємо ім'я користувача"""
        return self.name
    
    def get_token(self):
        """Отримуємо токен користувача"""
        return self.token
    
    def get_is_temp_password(self):
        """Отримуємо статус тимчасового пароля"""
        return self.is_temp_password
    
    def set_token(self, token): 
        """Встановлюємо токен користувача"""
        self.token = token

    def password_is_changed(self):
        self.is_temp_password=False

    def is_admin(self):
        """Перевіряємо, чи є користувач адміністратором"""
        return self.role == "admin"

    def is_manager(self):
        """Перевіряємо, чи є користувач менеджером"""
        return self.role == "manager"
    
    def is_employee(self):
        """Перевіряємо, чи є користувач співробітником"""
        return self.role == "employee"

    def clear_user_data(self):
        """Очищаємо дані користувача після виходу"""
        self.user_id = None
        self.name = None
        self.token = None
        self.role = None
        self.is_temp_password = None
