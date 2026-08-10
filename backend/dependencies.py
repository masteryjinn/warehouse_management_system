from fastapi import Depends
import auth.access_control as access_control
from auth.credentials import get_user_config
from config.token import verify_token

def get_config_and_check_all_roles(token_data: dict = Depends(verify_token)):
    user_id = token_data.get("user_id")
    role = token_data.get("role")
    access_control.check_acess_all_roles(user_id, role)
    return get_user_config(user_id)

def get_config_and_check_admin(token_data: dict = Depends(verify_token)):
    user_id = token_data.get("user_id")
    role = token_data.get("role")
    access_control.check_access_admin(user_id, role)
    return get_user_config(user_id)

def get_config_and_check_admin_and_manager(token_data: dict = Depends(verify_token)):
    user_id = token_data.get("user_id")
    role = token_data.get("role")
    access_control.check_access_admin_and_manager(user_id, role)
    return get_user_config(user_id)
