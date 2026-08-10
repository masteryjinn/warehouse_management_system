from fastapi import APIRouter, Depends, HTTPException, File, UploadFile
from fastapi.responses import FileResponse
import dependencies as deps
import utils.backups as backups
from logs.logger import action_logger

backups_router = APIRouter(prefix="/backups", tags=["Backups"])


@backups_router.get("/")
async def get_backups(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    return {"backups": backups.list_backups()}


@backups_router.post("/")
async def make_backup(
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    try:
        filename = backups.create_backup()
        action_logger.info(f"[BACKUP] Користувач '{USER_CONFIG['user']}' створив бекап бази даних: {filename}")
        return {"message": "Бекап створено", "filename": filename}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@backups_router.get("/download")
async def download_backup(
    filename: str,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    try:
        file_path = backups.get_backup_file_path(filename)
        
        # Використовуємо стандартний FileResponse
        return FileResponse(
            path=file_path,
            filename=filename,
            media_type="application/gzip"  # або "application/octet-stream"
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@backups_router.post("/restore-file")
async def restore_from_file(
    file: UploadFile = File(...),
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    try:
        content = await file.read()
        # Передаємо зчитані байти в модуль відновлення
        backups.restore_from_file(content)
        action_logger.info(f"[BACKUP RESTORE FILE] Користувач '{USER_CONFIG['user']}' відновив базу з файлу {file.filename}")
        return {"message": "Базу даних відновлено з завантаженого файлу"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@backups_router.post("/restore")
async def restore_from_backup(
    filename: str,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    try:
        backups.restore_backup(filename)
        action_logger.info(f"[BACKUP RESTORE] Користувач '{USER_CONFIG['user']}' відновив базу з бекапу: {filename}")
        return {"message": f"Базу даних відновлено з {filename}"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@backups_router.delete("/")
async def remove_backup(
    filename: str,
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin)
):
    try:
        backups.delete_backup(filename)
        action_logger.info(f"[BACKUP DELETE] Користувач '{USER_CONFIG['user']}' видалив бекап: {filename}")
        return {"message": f"Файл {filename} видалено"}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Файл не знайдено")
    except RuntimeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))