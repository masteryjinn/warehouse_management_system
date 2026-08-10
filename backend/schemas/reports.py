from pydantic import BaseModel
from datetime import date
from typing import Optional

class ReportRequestParams(BaseModel):
    start_date: date
    end_date: date
    status: str
    category: Optional[str] = None