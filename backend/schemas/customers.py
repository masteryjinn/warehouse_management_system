from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
import enum

class SupplierTypeEnum(str, enum.Enum):
    BUSINESS = "business"
    INDIVIDUAL = "individual"

class CustomerContacts(BaseModel):
    email: Optional[EmailStr] = Field(default=None, description="Електронна пошта")
    phone: Optional[str] = Field(default=None, pattern=r'^\+?\d{7,15}$', description="Телефонний номер")
    address: Optional[str] = None

class CustomerCreateUpdate(BaseModel):
    name: str
    type: str
    contacts: CustomerContacts

class CustomerImport(BaseModel):
    customers: list[CustomerCreateUpdate]

class CustomerFilter(BaseModel):
    search: Optional[str] = None
    name_filter: Optional[str] = None
    type_filter: Optional[SupplierTypeEnum] = None 
    email_required: Optional[bool] = None
    phone_required: Optional[bool] = None
    address_required: Optional[bool] = None