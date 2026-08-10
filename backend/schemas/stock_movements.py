from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date

class StockMovementFilterParams(BaseModel):
    movement_type: Optional[str] = None
    product_id: Optional[int] = Field(None, ge=1)
    section_id: Optional[int] = Field(None, ge=1)
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    quantity_min: Optional[int] = Field(None, ge=0)
    quantity_max: Optional[int] = Field(None, ge=0)

class IncomingItem(BaseModel):
    product_id: int
    quantity: int = Field(gt=0, description="Кількість для прийому повинна бути більше 0")
    unit: str
    section: str
    purchase_price: float = Field(gt=0, description="Ціна закупівлі повинна бути більше 0") 

class RelocationItem(BaseModel):
    product_id: int
    quantity: int = Field(ge=0, description="Кількість для переміщення повинна бути не менше 0")
    current_section: str

class RelocationRequest(BaseModel):
    section_id: int
    items: List[RelocationItem]

class WriteOffItem(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0, description="Кількість для списання повинна бути більше 0")
    reason: str
    section_id: int  

class WriteOffRequest(BaseModel):
    items: List[WriteOffItem]