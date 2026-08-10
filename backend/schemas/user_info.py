from pydantic import BaseModel

class UserInfo(BaseModel):
    employee_id: int
    name: str
    position: str | None
    email: str
    phone: str
    address: str