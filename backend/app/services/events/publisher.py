import json
from app.core.redis import get_redis_client
from app.schemas.events import EventEnvelope

class EventPublisher:
    def publish(self, stream: str, envelope: EventEnvelope) -> str | None:
        try:
            client = get_redis_client()
            return client.xadd(stream, {
                "event_id": envelope.event_id,
                "event_type": envelope.event_type,
                "tenant_id": envelope.tenant_id,
                "payload": json.dumps(envelope.payload, separators=(",", ":")),
                "created_at": envelope.created_at.isoformat(),
            })
        except Exception:
