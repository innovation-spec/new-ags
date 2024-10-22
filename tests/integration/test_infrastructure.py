import asyncio
import os

import pytest

RUN = os.getenv("RUN_INFRA_TESTS") == "1"
pytestmark = pytest.mark.skipif(not RUN, reason="set RUN_INFRA_TESTS=1 against a running Docker Compose stack")


def test_redis_stream_round_trip():
    import redis

