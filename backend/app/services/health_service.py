from ..logging_utils import get_logger

logger = get_logger(__name__)


class HealthService:
    def health_check(self) -> dict[str, str]:
        logger.info("Health check: status=ok")
        return {"status": "ok", "service": "interview-bot-backend"}


health_service = HealthService()
