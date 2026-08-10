from fastapi import APIRouter, Depends, HTTPException
from datetime import date
import dependencies as deps
from logs.logger import action_logger
import database.analytics_advanced as analytics

analytics_router = APIRouter(prefix="/analytics", tags=["Advanced Analytics"])


@analytics_router.get("/advanced")
async def get_advanced_analytics(
    metric: str, 
    start_date: date = None,
    end_date: date = None, 
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    """
    Отримати професійну аналітику складу.
    
    Метрики:
    - abc_analysis: ABC-аналіз товарів за оборотом
    - xyz_analysis: XYZ-аналіз стабільності попиту
    - abc_xyz_matrix: Комбінована ABC-XYZ матриця
    - turnover: Аналіз оборотності товарів
    - critical_stock: Критичні залишки з рекомендаціями
    - sales_trend: Тренд продажів
    - write_offs: Аналіз списань
    - warehouse_efficiency: Показники ефективності складу
    """
    try:
        if metric == "abc_analysis":
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Start and end dates required")
            data = analytics.get_abc_analysis(USER_CONFIG, start_date, end_date)
            
        elif metric == "xyz_analysis":
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Start and end dates required")
            data = analytics.get_xyz_analysis(USER_CONFIG, start_date, end_date)
            
        elif metric == "abc_xyz_matrix":
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Start and end dates required")
            data = analytics.get_abc_xyz_matrix(USER_CONFIG, start_date, end_date)
            
        elif metric == "turnover":
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Start and end dates required")
            data = analytics.get_turnover_analysis(USER_CONFIG, start_date, end_date)
            
        elif metric == "critical_stock":
            data = analytics.get_critical_stock_advanced(USER_CONFIG)
            
        elif metric == "sales_trend":
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Start and end dates required")
            data = analytics.get_sales_data(USER_CONFIG, start_date, end_date)
            
        elif metric == "write_offs":
            if not start_date or not end_date:
                raise HTTPException(status_code=400, detail="Start and end dates required")
            data = analytics.get_write_offs_data(USER_CONFIG, start_date, end_date)
            
        elif metric == "warehouse_efficiency":
            metrics = analytics.get_warehouse_efficiency(USER_CONFIG)
            action_logger.info(
                f"[ANALYTICS] Користувач ID: {USER_CONFIG['user']} отримав метрики ефективності складу"
            )
            return {"metric": metric, "metrics": metrics}
            
        else:
            raise HTTPException(status_code=400, detail="Unknown metric")

        action_logger.info(
            f"[ANALYTICS] Користувач ID: {USER_CONFIG['user']} отримав дані аналітики: {metric}"
        )
        print("DATA:", data)
        print("METRIC:", metric)
        
        return {"metric": metric, "values": data}
        
    except Exception as e:
        action_logger.error(
            f"[ANALYTICS ERROR] Користувач ID: {USER_CONFIG['user']}, метрика: {metric}, помилка: {str(e)}"
        )
        raise HTTPException(status_code=500, detail=f"Analytics error: {str(e)}")