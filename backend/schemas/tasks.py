from pydantic import BaseModel, Field
from typing import Optional
from datetime import date
import enum

class TaskStatusEnum(str, enum.Enum):
    """
    Перелік можливих статусів для завдань у системі.
    """
    # Нове завдання, щойно створене
    NEW = "new" 
    
    # Завдання, яке знаходиться в роботі у призначеного працівника
    IN_PROGRESS = "in_progress" 
    
    # Завдання виконане працівником і очікує перевірки менеджером/адміністратором
    UNDER_REVIEW = "under_review" 
    
    # Завдання успішно завершене
    COMPLETED = "completed" 
    
    # Завдання скасоване (менеджером або адміністратором)
    CANCELLED = "cancelled"
    

class TaskCreateUpdate(BaseModel):
    title: str = Field(min_length=3, max_length=255)
    description: Optional[str] = None
    priority: str = Field(pattern=r'^(low|medium|high)$', description="Пріоритет: low, medium або high")
    deadline: str = Field(description="Кінцева дата виконання у форматі YYYY-MM-DD HH:MM")
    max_assignees: int = Field(default=1, ge=1, description="Максимальна кількість виконавців (за замовчуванням 1)")

class TaskStatusUpdate(BaseModel):
    status: TaskStatusEnum = Field(description="Новий статус завдання")

class TaskFilterParams(BaseModel):
    """Модель для збору всіх параметрів фільтрації завдань із Query Parameters."""
    
    # Фільтри за статусом/пріоритетом
    status_tab: Optional[str] = Field(None, description="Фільтр за вкладкою (наприклад, 'my_tasks')") 
    status: Optional[TaskStatusEnum] = None 
    priority: Optional[str] = Field(None, pattern=r'^(low|medium|high)$', description="Фільтр за пріоритетом: low, medium або high")
    
    # Фільтр за виконавцем
    employee_id: Optional[int] = Field(None, ge=1)
    
    # Фільтри за датами
    # Використання date автоматично валідує формат YYYY-MM-DD
    start_date: Optional[date] = None 
    end_date: Optional[date] = None
    
    # Загальний пошук
    search: Optional[str] = None