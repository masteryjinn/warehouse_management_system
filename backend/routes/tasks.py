from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
import math
from config.token import verify_token
import dependencies as deps
import database.tasks as db_tasks
from logs.logger import action_logger
from schemas.tasks import TaskCreateUpdate, TaskStatusEnum, TaskStatusUpdate, TaskFilterParams
from auth.access_control import check_access_admin_and_manager

tasks_router = APIRouter(prefix="/tasks", tags=["tasks"])

@tasks_router.get("/")
async def read_tasks(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    filters: TaskFilterParams = Depends(TaskFilterParams)
):
    # exclude_none=True гарантує, що ми не передаємо None-значення, які можуть зламати DAL
    filter_data = filters.model_dump(exclude_none=True, by_alias=True)
    tasks, total_count = db_tasks.get_tasks(
            config=USER_CONFIG,
            page=page,
            page_size=page_size,
            **filter_data
        )

    total_pages = math.ceil(total_count / page_size)
    return {
        "tasks": tasks,
        "total_pages": total_pages,
        "current_page": page,
    }

@tasks_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_task(
    task_data: TaskCreateUpdate = Body(...),
    token_data: dict = Depends(verify_token),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    try:
        task_id = db_tasks.create_task_in_db(
            USER_CONFIG,
            task_data,
            token_data['user_id']
        )
        action_logger.info(f"Завдання '{task_data.title}' створено користувачем '{USER_CONFIG['user']}'")
        return {"message": "Task created", "task_id": task_id}
    except Exception as e:
        print(f"[create_task] ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tasks_router.patch("/{task_id}/status")
async def update_status(
    task_id: int, 
    data: TaskStatusUpdate, # Pydantic валідація статусу
    # 1. Залежність для отримання user_id/role
    token_data: dict = Depends(verify_token), 
    # 2. Залежність для отримання Конфігурації БД (з вбудованою перевіркою всіх ролей)
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles) 
):
    user_id = token_data.get("user_id")
    role = token_data.get("role")
    new_status = data.status.value 

    # 1. Спеціальна логіка для "під наглядом/на перевірці"
    if new_status == TaskStatusEnum.UNDER_REVIEW:
        if role != "employee":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Лише працівники можуть встановлювати статус 'на перевірці'"
            )

        # Перевірка, чи призначений користувач (вимагає, щоб USER_CONFIG містив user_id)
        if not db_tasks.is_user_assigned_to_task(USER_CONFIG, task_id, user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="Ви не призначені до цього завдання"
            )
            
    # 2. Логіка для всіх інших статусів (Admin/Manager)
    elif new_status in [
        TaskStatusEnum.COMPLETED, 
        TaskStatusEnum.CANCELLED,
        TaskStatusEnum.NEW,
        TaskStatusEnum.IN_PROGRESS
    ]:
    # Використовуємо пряму перевірку, оскільки вона не залежить від USER_CONFIG
        check_access_admin_and_manager(user_id, role)
    
    # 3. Оновлення статусу
    success = db_tasks.update_task_status_in_db(USER_CONFIG, task_id, new_status)
    if not success:
        action_logger.error(f"[TASK STATUS UPDATE ERROR] Не вдалося оновити статус завдання ID={task_id}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Не вдалося оновити статус")
        
    action_logger.info(f"Статус завдання ID: {task_id} змінено на '{new_status}' користувачем: {USER_CONFIG['user']}")
    return {"message": "Статус оновлено"}

@tasks_router.post("/{task_id}/assign")
async def assign_task(
    task_id: int, 
    token_data: dict = Depends(verify_token),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles)
):
    user_id = token_data.get("user_id")

    success = db_tasks.assign_task_to_user(USER_CONFIG, task_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot assign task")

    # Автоматична зміна статусу на 'in_progress'
    db_tasks.update_task_status_in_db(USER_CONFIG, task_id, "in_progress")
    action_logger.info(f"Завдання ID: {task_id} призначено користувачу'{USER_CONFIG['user']}' та статус змінено на 'in_progress'")
    return {"message": "Task assigned and status set to in_progress"}

@tasks_router.post("/{task_id}/unassign")
async def unassign_task(
    task_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_all_roles)
):
    user_id = USER_CONFIG.get("user_id")
    success = db_tasks.unassign_task_from_user(USER_CONFIG, task_id, user_id)
    if not success:
        raise HTTPException(status_code=400, detail="Cannot unassign task")
    action_logger.info(f"Завдання ID: {task_id} розпризначено користувачу '{USER_CONFIG['user']}'")
    return {"message": "Task unassigned"}

@tasks_router.delete("/{task_id}")
async def delete_task(
    task_id: int, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    try:
        success = db_tasks.delete_task_from_db(USER_CONFIG, task_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Завдання не знайдено")
            
        action_logger.info(f"Завдання ID: {task_id} видалено користувачем ID: {USER_CONFIG['user']}")
        return {"message": "Task deleted"}

    except ValueError as e:
        # Відловлюємо нашу заборону на видалення
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        # Відловлюємо всі інші технічні помилки
        print(f"Server Error: {e}")
        raise HTTPException(status_code=500, detail="Внутрішня помилка сервера при видаленні")