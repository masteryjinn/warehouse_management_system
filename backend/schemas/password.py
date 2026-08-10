from pydantic import BaseModel, Field, EmailStr

# Сценарій 1: Зміна пароля (авторизований користувач)
class ChangePasswordRequest(BaseModel):
    # Додаємо валідацію: мінімальна довжина 8, має бути строгим (Field)
    new_password: str = Field(
        min_length=8,
        description="Новий пароль. Рекомендовано не менше 8 символів."
    )

# Сценарій 2: Зміна пароля після скидання (з тимчасового)
class PasswordUpdateAfterResetRequest(BaseModel):
    # Додаємо валідацію: мінімальна довжина 8
    user_id: int = Field(
        description="Унікальний ідентифікатор користувача."
    )
    new_password: str = Field(
        min_length=8,
        description="Новий постійний пароль. Рекомендовано не менше 8 символів."
    )

# Сценарій 3: Запит на скидання (надсилання листа)
class PasswordResetRequest(BaseModel):
    # Використовуємо EmailStr для автоматичної перевірки формату email
    email: EmailStr = Field(
        description="Електронна адреса користувача для відновлення доступу."
    )