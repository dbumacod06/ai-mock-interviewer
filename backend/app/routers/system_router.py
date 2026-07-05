from fastapi import APIRouter

from ..logging_utils import get_logger
from ..services import health_service, status_service

router = APIRouter(tags=["system"])
logger = get_logger(__name__)


@router.get("/health")
def health_check() -> dict[str, str]:
    logger.info("Health check endpoint called")
    return health_service.health_check()


@router.get("/api/status")
def status() -> dict[str, str]:
    logger.info("Status endpoint called")
    return status_service.get_status()
