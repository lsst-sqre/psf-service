"""Tests for async job creation."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

import pytest
from dramatiq import Worker

from vocutouts.broker import broker

if TYPE_CHECKING:
    from typing import Dict, List

    from httpx import AsyncClient


PENDING_JOB = """
<uws:job
    version="1.1"
    xsi:schemaLocation="http://www.ivoa.net/xml/UWS/v1.0 UWS.xsd"
    xmlns:xml="http://www.w3.org/XML/1998/namespace"
    xmlns:uws="http://www.ivoa.net/xml/UWS/v1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <uws:jobId>1</uws:jobId>
  <uws:ownerId>someone</uws:ownerId>
  <uws:phase>PENDING</uws:phase>
  <uws:creationTime>[DATE]</uws:creationTime>
  <uws:executionDuration>600</uws:executionDuration>
  <uws:destruction>[DATE]</uws:destruction>
  <uws:parameters>
    <uws:parameter id="id" isPost="true">1:2:band:value</uws:parameter>
    <uws:parameter id="pos" isPost="true">CIRCLE 0 1 2</uws:parameter>
  </uws:parameters>
</uws:job>
"""

COMPLETED_JOB = """
<uws:job
    version="1.1"
    xsi:schemaLocation="http://www.ivoa.net/xml/UWS/v1.0 UWS.xsd"
    xmlns:xml="http://www.w3.org/XML/1998/namespace"
    xmlns:uws="http://www.ivoa.net/xml/UWS/v1.0"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <uws:jobId>2</uws:jobId>
  <uws:runId>some-run-id</uws:runId>
  <uws:ownerId>someone</uws:ownerId>
  <uws:phase>COMPLETED</uws:phase>
  <uws:creationTime>[DATE]</uws:creationTime>
  <uws:startTime>[DATE]</uws:startTime>
  <uws:endTime>[DATE]</uws:endTime>
  <uws:executionDuration>600</uws:executionDuration>
  <uws:destruction>[DATE]</uws:destruction>
  <uws:parameters>
    <uws:parameter id="id" isPost="true">1:2:band:value</uws:parameter>
    <uws:parameter id="pos" isPost="true">CIRCLE 0.5 0.8 2</uws:parameter>
  </uws:parameters>
  <uws:results>
    <uws:result id="cutout" xlink:href="https://example.com/cutout-result"\
 mime-type="application/fits"/>
  </uws:results>
</uws:job>
"""


@pytest.mark.asyncio
async def test_create_job(client: AsyncClient) -> None:
    r = await client.post(
        "/cutout/jobs",
        headers={"X-Auth-Request-User": "someone"},
        data={"ID": "1:2:band:value", "Pos": "CIRCLE 0 1 2"},
    )
    assert r.status_code == 303
    assert r.headers["Location"] == "https://example.com/cutout/jobs/1"
    r = await client.get(
        "/cutout/jobs/1", headers={"X-Auth-Request-User": "someone"}
    )
    assert r.status_code == 200
    result = re.sub(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", "[DATE]", r.text)
    assert result == PENDING_JOB.strip()

    # Start a worker.
    worker = Worker(broker, worker_timeout=100)
    worker.start()

    # Try again but immediately queuing the job to run.
    try:
        r = await client.post(
            "/cutout/jobs",
            headers={"X-Auth-Request-User": "someone"},
            data={
                "ID": "1:2:band:value",
                "pos": "CIRCLE 0.5 0.8 2",
                "runid": "some-run-id",
            },
            params={"phase": "RUN"},
        )
        assert r.status_code == 303
        assert r.headers["Location"] == "https://example.com/cutout/jobs/2"
        r = await client.get(
            "/cutout/jobs/2",
            headers={"X-Auth-Request-User": "someone"},
            params={"wait": 2, "phase": "QUEUED"},
        )
        assert r.status_code == 200
        if "EXECUTING" in r.text:
            r = await client.get(
                "/cutout/jobs/2",
                headers={"X-Auth-Request-User": "someone"},
                params={"wait": 10, "phase": "EXECUTING"},
            )
            assert r.status_code == 200
        result = re.sub(r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ", "[DATE]", r.text)
        assert result == COMPLETED_JOB.strip()
    finally:
        worker.stop()


@pytest.mark.asyncio
async def test_bad_parameters(client: AsyncClient) -> None:
    bad_params: List[Dict[str, str]] = [
        {},
        {"pos": "RANGE 0 360 -2 2"},
        {"id": "foo", "foo": "bar"},
        {"id": "foo", "pos": "RANGE 0 360"},
        {"id": "foo", "pos": "POLYHEDRON 10"},
        {"id": "foo", "pos": "CIRCLE 1 1"},
        {"id": "foo", "pos": "POLYGON 1 1"},
        {"id": "foo", "circle": "1 1 1", "pos": "RANGE 0 360 1"},
        {"id": "foo", "circle": "1"},
        {"id": "foo", "polygon": "1 2 3"},
        {"id": "foo", "circle": "1 1 1", "phase": "STOP"},
        {"id": "foo", "circle": "1 1 1", "PHASE": "STOP"},
        {"ID": "some-id", "pos": "RANGE 1 1 2 2", "phase": "RUN"},
    ]
    for params in bad_params:
        r = await client.post(
            "/cutout/jobs",
            headers={"X-Auth-Request-User": "user"},
            data=params,
        )
        assert r.status_code == 422, f"Parameters {params}"
        assert r.text.startswith("UsageError")