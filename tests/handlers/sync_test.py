"""Tests for sync cutout requests."""

from __future__ import annotations

import pytest
from dramatiq import Worker
from httpx import AsyncClient

from vocutouts.broker import broker


@pytest.mark.asyncio
async def test_sync(client: AsyncClient) -> None:
    worker = Worker(broker, worker_timeout=100)
    worker.start()

    try:
        # GET request.
        r = await client.get(
            "/api/cutout/sync",
            headers={"X-Auth-Request-User": "someone"},
            params={"ID": "1:2:band:id", "Pos": "CIRCLE 0 -2 2"},
        )
        assert r.status_code == 303
        assert r.headers["Location"] == "https://example.com/some/path"

        # POST request.
        r = await client.post(
            "/api/cutout/sync",
            headers={"X-Auth-Request-User": "someone"},
            data={"ID": "3:4:band:id", "Pos": "CIRCLE 0 -2 2"},
        )
        assert r.status_code == 303
        assert r.headers["Location"] == "https://example.com/some/path"
    finally:
        worker.stop()


@pytest.mark.asyncio
async def test_bad_parameters(client: AsyncClient) -> None:
    bad_params: list[dict[str, str]] = [
        {},
        {"pos": "RANGE 0 360 -2 2"},
        {"id": "5:6:a:b", "foo": "bar"},
        {"id": "5:6:a:b", "pos": "RANGE 0 360"},
        {"id": "5:6:a:b", "pos": "POLYHEDRON 10"},
        {"id": "5:6:a:b", "pos": "CIRCLE 1 1"},
        {"id": "5:6:a:b", "pos": "POLYGON 1 1"},
        {"id": "5:6:a:b", "circle": "1 1 1", "pos": "RANGE 0 360 1"},
        {"id": "5:6:a:b", "circle": "1"},
        {"id": "5:6:a:b", "polygon": "1 2 3"},
        {"id": "5:6:a:b", "circle": "1 1 1", "phase": "STOP"},
        {"id": "5:6:a:b", "circle": "1 1 1", "PHASE": "STOP"},
    ]
    for params in bad_params:
        r = await client.get(
            "/api/cutout/sync",
            headers={"X-Auth-Request-User": "user"},
            params=params,
        )
        assert r.status_code == 422, f"Parameters {params}"
        assert r.text.startswith("UsageError")
        r = await client.post(
            "/api/cutout/sync",
            headers={"X-Auth-Request-User": "user"},
            data=params,
        )
        assert r.status_code == 422, f"Parameters {params}"
        assert r.text.startswith("UsageError")
