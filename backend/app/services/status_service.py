from ..logging_utils import get_logger

logger = get_logger(__name__)


class StatusService:
    def get_status(self) -> dict[str, str]:
        logger.info("Status check: mode=voice-assistant, stt=Whisper")
        return {
            "mode": "voice-assistant",
            "stt": "Whisper",
            "tts": "planned",
            "llm": "planned",
        }


status_service = StatusService()
