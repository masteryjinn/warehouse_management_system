from fastapi import HTTPException

def check_access_admin_and_manager(user_id: int, role: str):
    if role not in ["admin", "manager"]:
        raise HTTPException(status_code=403, detail="Недостатньо прав для виконання цієї дії")
    if not user_id:
        raise HTTPException(status_code=400, detail="Некоректний токен")
    
def check_access_admin(user_id: int, role: str):
    if role != "admin":
        raise HTTPException(status_code=403, detail="Недостатньо прав для виконання цієї дії")
    if not user_id:
        raise HTTPException(status_code=400, detail="Некоректний токен")

def check_access_manager(user_id: int, role: str):
    if role != "manager":
        raise HTTPException(status_code=403, detail="Недостатньо прав для виконання цієї дії")
    if not user_id:
        raise HTTPException(status_code=400, detail="Некоректний токен")
    
def check_acess_all_roles(user_id: int, role: str):
    if role not in ["admin", "manager", "employee"]:
        raise HTTPException(status_code=403, detail="Недостатньо прав для виконання цієї дії")
    if not user_id:
        raise HTTPException(status_code=400, detail="Некоректний токен")