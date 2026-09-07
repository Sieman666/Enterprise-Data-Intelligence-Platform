import logging

from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError

from app.schemas.analytics import KPIReport, ProfileReport, TrendReport
from app.services.analytics import get_kpi_report, get_profile_report, get_trend_report

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/kpis", response_model=KPIReport)
def read_kpis() -> dict:
    try:
        return get_kpi_report()
    except SQLAlchemyError as exc:
        logger.exception("Failed to generate KPI report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc


@router.get("/trends", response_model=TrendReport)
def read_trends() -> dict:
    try:
        return get_trend_report()
    except SQLAlchemyError as exc:
        logger.exception("Failed to generate trend report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc


@router.get("/profile", response_model=ProfileReport)
def read_profile() -> dict:
    try:
        return get_profile_report()
    except SQLAlchemyError as exc:
        logger.exception("Failed to generate profile report")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {exc}",
        ) from exc
