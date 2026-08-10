from typing import List, Optional
from pydantic import BaseModel

class OrderItem(BaseModel):
    product_id: int
    quantity: int
    unit: str
    price: float
    section: str

class ConfirmOrderRequest(BaseModel):
    items: List[OrderItem]

class OrderFilterParams(BaseModel):
    search: Optional[str] = None
    customer_name_filter: Optional[str] = None
    status_filter: Optional[str] = None
    date_min: Optional[str] = None
    date_max: Optional[str] = None

class OrderCreate(BaseModel):
    customer_id: int

class BulkShipRequest(BaseModel):
    order_ids: List[int]