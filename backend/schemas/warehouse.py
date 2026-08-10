from pydantic import BaseModel, Field

class SectionCreateUpdate(BaseModel):
    name: str = Field(min_length=3, max_length=100, description="Назва секції")
    location: str = Field(description="Місцезнаходження секції")
    employee_name: str | None = Field(default=None, description="Ім'я відповідального працівника")
