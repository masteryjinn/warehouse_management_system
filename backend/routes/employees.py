from os import name
from fastapi import APIRouter, HTTPException, Depends
from schemas.employees import RegisterRequest, EmployeeCreateUpdate, EmployeeImport, EmployeeUpdateRole
from auth.hashing import get_hash_password
import database.employees as emp_db
import database.auth as auth_db
from fastapi import Query
import dependencies as deps
from logs.logger import action_logger

employees_router = APIRouter(prefix="/employees", tags=["Employees"])

@employees_router.post("/register/{emp_id}")
async def register_user(
    emp_id: int, 
    request: RegisterRequest, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)):
    """
    Реєстрація користувача (створення запису користувача)
    :param emp_id: ID співробітника
    :param request: дані для реєстрації (username, password)
    :param USER_CONFIG: Конфігурація користувача
    """

    # Отримуємо дані з запиту
    username_r = request.username
    password_r = request.password
    role_r = request.role
    # Перевірка наявності ID співробітника
    if not emp_id:
        raise HTTPException(status_code=400, detail="ID співробітника обов'язковий для заповнення")    

    # Перевірка наявності пароля та імені користувача
    if not username_r or not password_r:
        raise HTTPException(status_code=400, detail="Логін та пароль обов'язкові для заповнення")

    # Хешуємо пароль для безпечного зберігання в базі
    password_hash_r = get_hash_password(password_r)

    # Додаємо нового користувача до бази даних
    user_added = emp_db.add_user_to_db(USER_CONFIG, username_r, password_hash_r, emp_id, role_r)

    if user_added is False:
        raise HTTPException(status_code=500, detail="Не вдалося зареєструвати користувача. Можливо, користувач з таким логіном вже існує")
    
    user_registered = emp_db.register_user_in_db(username_r, password_hash_r, role_r)

    if not user_registered:
        raise HTTPException(status_code=500, detail="Не вдалося зареєструвати користувача в базі даних")
    action_logger.info(f"[REGISTER] Користувач '{USER_CONFIG['user']}' зареєстрував нового користувача '{request.username}' для співробітника ID={emp_id} з роллю '{request.role}'")
    return {"message": "Користувача успішно зареєстровано"}

@employees_router.get("/")
async def get_employees(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str = Query(None),
    registered_only: bool = Query(False)
):
    total_items = emp_db.count_total_employees(USER_CONFIG, search, registered_only)
    total_pages = max((total_items + limit - 1) // limit, 1)

    if page > total_pages:
        raise HTTPException(status_code=400, detail="Сторінка виходить за межі")

    employees = emp_db.get_employees_function(USER_CONFIG, page, limit, search, registered_only)

    return {
        "data": employees,
        "total_pages": total_pages,
        "total_items": total_items,
        "current_page": page
    }


@employees_router.put("/{emp_id}")
async def update_employee(
    emp_id: int,
    data: EmployeeCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    contacts_dict = data.contacts.model_dump(exclude_none=True)
    emp_db.update_employee_function(USER_CONFIG, emp_id, data.name, data.position, contacts_dict)
    action_logger.info(f"[UPDATE EMPLOYEE] Користувач '{USER_CONFIG['user']}' оновив дані співробітника ID={emp_id}, ім’я='{data.name}'")
    return {"message": "Дані співробітника оновлено"}


@employees_router.delete("/{emp_id}")
async def remove_employee(
    emp_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    username = auth_db.get_username_by_emp_id(emp_id)
    if username== USER_CONFIG['user']:
        raise HTTPException(status_code=400, detail="Не можна видалити самого себе")
    # Видаляємо працівника у будь-якому випадку
    emp_db.delete_employee_function(USER_CONFIG, emp_id)

    # Якщо користувач був зареєстрований — пробуємо видалити акаунт
    if username:
        user_deleted = emp_db.delete_user_from_db(username)
        user_deleted2=emp_db.delete_employee_account_function(USER_CONFIG, emp_id)
        if not user_deleted and not user_deleted2:
            raise HTTPException(status_code=500, detail="Співробітника видалено, але не вдалося видалити обліковий запис користувача")
        action_logger.info(f"[DELETE EMPLOYEE+USER] Користувач '{USER_CONFIG['user']}' видалив співробітника ID={emp_id} та обліковий запис '{username}'")
        return {"message": "Зареєстрованого співробітника та його обліковий запис успішно видалено"}
    else:
        action_logger.info(f"[DELETE EMPLOYEE] Користувач '{USER_CONFIG['user']}' видалив незареєстрованого співробітника ID={emp_id}")
        return {"message": "Незареєстрованого співробітника успішно видалено"}

@employees_router.post("/")
async def add_employee(
    data: EmployeeCreateUpdate,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    contacts = data.contacts.model_dump(exclude_none=True)
    emp_id = emp_db.add_employee_function(USER_CONFIG, data.name, data.position, contacts)
    action_logger.info(f"[ADD EMPLOYEE] Користувач '{USER_CONFIG['user']}' додав співробітника ID={emp_id}, ім’я='{data.name}'")
    return {"message": "Співробітника додано"}

@employees_router.put("/update_role/{employee_id}")
async def update_role(
    employee_id: int,
    data: EmployeeUpdateRole,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    new_role = data.role 
    if not employee_id or not new_role:
        raise HTTPException(status_code=400, detail="ID співробітника та нова роль обов'язкові")
    
    username = auth_db.get_username_by_emp_id(employee_id)
    if username == USER_CONFIG['user']:
        raise HTTPException(status_code=400, detail="Не можна змінити свою власну роль")

    if new_role not in ["admin", "manager", "employee"]:
        raise HTTPException(status_code=400, detail="Некоректна роль")

    username = auth_db.get_username_by_emp_id(employee_id)
    if not username:
        raise HTTPException(status_code=404, detail="Співробітника не знайдено")

    if not emp_db.update_user_role_in_db(USER_CONFIG, employee_id, new_role):
        raise HTTPException(status_code=500, detail="Не вдалося оновити роль у таблиці користувачів")

    # Призначення ролі в MySQL (GRANT)
    if not emp_db.grant_role_to_user(username, new_role):
        raise HTTPException(status_code=500, detail="Не вдалося призначити роль у MySQL")
    action_logger.info(f"[UPDATE ROLE] Користувач '{USER_CONFIG['user']}' змінив роль користувачу '{username}' (співробітник ID={employee_id}) на '{new_role}'")
    return {"message": f"Роль '{new_role}' успішно оновлено для користувача '{username}'"}

@employees_router.get("/role/{employee_id}")
async def get_employee_role(
    employee_id: int,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    role = emp_db.get_employee_role_from_db(employee_id)
    if role is None:
        raise HTTPException(status_code=404, detail="Співробітника не знайдено або він не має ролі")
    return {"role": role}

@employees_router.get("/select")
async def get_employees_select(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    employees=emp_db.get_employees_full(USER_CONFIG)
    if not employees:
        raise HTTPException(status_code=404, detail="Працівники не знайдені")
    print(f"Отримано {len(employees)} працівників для селекту")
    print(f"Перший працівник: {employees[0] if employees else 'Немає працівників'}")    
    return {"employees": employees}

@employees_router.post("/import")
async def import_suppliers(
    data: EmployeeImport,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):

    imported_count = 0
    skipped_count = 0
    imported_names = []
    skipped_names = []

    for item in data.employees:
        contacts = item.contacts.model_dump(exclude_none=True)
        result = emp_db.add_employee_function(USER_CONFIG, item.name, item.position, contacts)
        if result is not None:
            imported_count += 1
            imported_names.append(item.name)
        else:
            skipped_count += 1
            skipped_names.append(item.name)
    action_logger.info(
        f"[IMPORT EMPLOYEES] Користувач '{USER_CONFIG['user']}' імпортував {imported_count} нових, "
        f"пропущено {skipped_count}"
    )

    return {
        "message": f"Імпортовано {imported_count}, пропущено {skipped_count}",
        "imported_names": imported_names,
        "skipped_names": skipped_names
    }
