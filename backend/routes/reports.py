# main.py
from fastapi import APIRouter, Depends, Query
from typing import Annotated
from database.reports import get_report_data
from logs.logger import action_logger
import dependencies as deps
from schemas.reports import ReportRequestParams

report_router = APIRouter()

@report_router.get("/orders-report")
async def get_orders_report(
    parameters: Annotated[ReportRequestParams, Query()],
    USER_CONFIG: dict = Depends(deps.get_config_and_check_admin_and_manager)
):
    params = parameters.model_dump(exclude_none=True)
    data, total_orders, total_items, total_revenue = get_report_data(
        USER_CONFIG, **params
    )
    action_logger.info(f"[REPORT] Користувач '{USER_CONFIG['user']}' отримав звіт по замовленням за період {params['start_date']} - {params['end_date']}")
    return {
        "data": data,
        "total_orders": total_orders,
        "total_items": total_items,
        "total_revenue": total_revenue,
    }
