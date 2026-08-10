from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List

# --- Enum для типу постачальника (якщо у вас фіксовані типи) ---
import enum
class SupplierTypeEnum(str, enum.Enum):
    MANUFACTURER = "manufacturer"
    WHOLESALER = "wholesaler"
    DISTRIBUTOR = "distributor"

# --- 1. Модель для контакту ---
class SupplierContacts(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="Електронна пошта")
    phone: Optional[str] = Field(default=None, pattern=r'^\+?\d{7,15}$', description="Телефонний номер")
    address: Optional[str] = None

# --- 2. Модель для POST/PUT ---
class SupplierCreateUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=150, description="Назва постачальника")
    # Використовуємо Enum для типу
    type: SupplierTypeEnum 
    # Вкладаємо контакти
    contacts: SupplierContacts 
    
# --- 3. Модель для Імпорту (список) ---
class SupplierImport(BaseModel):
    # У Body буде List[SupplierCreateUpdate]
    suppliers: List[SupplierCreateUpdate]

# --- 4. Модель для Фільтрації ---
class SupplierFilter(BaseModel):
    search: Optional[str] = None
    name_filter: Optional[str] = None
    type_filter: Optional[SupplierTypeEnum] = None 
    email_required: Optional[bool] = None
    phone_required: Optional[bool] = None
    address_required: Optional[bool] = None