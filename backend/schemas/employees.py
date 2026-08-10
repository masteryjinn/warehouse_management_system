from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str

class EmployeeContactInfo(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="Електронна пошта")
    phone: Optional[str] = Field(default=None, pattern=r'^\+?\d{7,15}$', description="Телефонний номер")
    address: Optional[str] = None

class EmployeeCreateUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=150, description="Ім'я співробітника")
    position: Optional[str] = Field(default=None, max_length=100, description="Посада співробітника")
    contacts: EmployeeContactInfo

class EmployeeImport(BaseModel):
    employees: list[EmployeeCreateUpdate]

class EmployeeUpdateRole(BaseModel):
    role: str = Field(description="Нова роль співробітника (admin, manager, employee)")