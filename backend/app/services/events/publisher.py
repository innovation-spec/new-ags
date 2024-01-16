import json
from app.core.redis import get_redis_client
from app.schemas.events import EventEnvelope

class EventPublisher:
    def publish(self, stream: str, envelope: EventEnvelope) -> str | None:
