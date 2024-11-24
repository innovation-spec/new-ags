import asyncio
import os

import pytest

RUN = os.getenv("RUN_INFRA_TESTS") == "1"
pytestmark = pytest.mark.skipif(not RUN, reason="set RUN_INFRA_TESTS=1 against a running Docker Compose stack")


def test_redis_stream_round_trip():
    import redis

    client = redis.Redis.from_url(os.getenv("REDIS_TEST_URL", "redis://localhost:16379/0"), decode_responses=True)
    assert client.ping() is True
    stream = "stream:integration-proof"
    event_id = client.xadd(stream, {"event_type": "integration.proof", "tenant_id": "tenant-a"})
    rows = client.xrange(stream, min=event_id, max=event_id)
    assert rows == [(event_id, {"event_type": "integration.proof", "tenant_id": "tenant-a"})]
    client.delete(stream)


def test_minio_required_buckets_exist():
    from minio import Minio

    client = Minio(
        os.getenv("MINIO_TEST_ENDPOINT", "localhost:19000"),
        access_key=os.getenv("MINIO_ACCESS_KEY", "agasthya"),
        secret_key=os.getenv("MINIO_SECRET_KEY", "agasthya-demo-secret"),
        secure=False,
    )
    expected = {
        "agasthya-models", "agasthya-datasets", "agasthya-artifacts",
        "agasthya-reports", "agasthya-state-archives",
    }
    assert expected.issubset({bucket.name for bucket in client.list_buckets()})


def test_temporal_server_is_reachable():
    async def probe():
        from temporalio.client import Client
        client = await Client.connect(os.getenv("TEMPORAL_TEST_ADDRESS", "localhost:17233"))
        # A connected client exposes its configured service client; successful
        # connect is the actual reachability assertion.
        assert client.service_client is not None

    asyncio.run(probe())
