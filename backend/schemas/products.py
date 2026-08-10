from typing import List, Optional
from pydantic import BaseModel, Field
from enum import Enum

category_name_to_id = {
    "Автотовари": 10,
    "Електроніка": 1,
    "Здоров’я та краса": 9,
    "Зоотовари": 12,
    "Іграшки та ігри": 8,
    "Їжа": 4,
    "Канцелярія": 6,
    "Книги": 5,
    "Меблі": 2,
    "Одяг": 3,
    "Побутова техніка": 7,
    "Побутова хімія": 14,
    "Сад та інструменти": 11,
    "Спорт та туризм": 13,
    "Технології": 15
}

# Словник категорій: назва -> ID
class SortOrder(str, Enum):
    price_asc = "price_asc"
    price_desc = "price_desc"
    quantity_asc = "quantity_asc"
    quantity_desc = "quantity_desc"
    name_asc = "name_asc"
    name_desc = "name_desc"
    expiration_date_asc = "expiration_date_asc"
    expiration_date_desc = "expiration_date_desc"

class ProductImport(BaseModel):
    product_id: Optional[int] = None
    name: str
    description: Optional[str] = None
    price: float
    quantity: int
    expiration_date: Optional[str] = None  
    unit: str
    category_name: Optional[str] = None
    supplier_name: Optional[str] = None
    section_name: Optional[str] = None

class ProductsImportRequest(BaseModel):
    products: List[ProductImport]

class ProductFilterParams(BaseModel):
    search: Optional[str] = None
    expire_date: Optional[bool] = None
    has_expired: Optional[bool] = None
    section: Optional[str] = None
    name_filter: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    sort_order: Optional[SortOrder] = None

class ProductCreateUpdate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    price: float = Field(gt=0)
    expiry_date: Optional[str] = None  # або date
    unit: str = Field(min_length=1, max_length=50)
    category: Optional[str] = None
    supplier_name: Optional[str] = None
    section_name: Optional[str] = None