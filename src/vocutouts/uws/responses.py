"""Return internal objects as XML responses."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from fastapi.templating import Jinja2Templates

if TYPE_CHECKING:
    from typing import List

    from fastapi import Request, Response

    from .models import Availability, Job, JobDescription, JobError

__all__ = ["UWSTemplates"]


def _isodatetime_filter(date: datetime) -> str:
    """Format a datetime according to the requirements of IVOA standards."""
    return date.strftime("%Y-%m-%dT%H:%M:%SZ")


_templates = Jinja2Templates(
    directory=str(Path(__file__).parent / "templates")
)
_templates.env.filters["isodatetime"] = _isodatetime_filter


class UWSTemplates:
    """Template responses for the UWS protocol."""

    def availability(
        self, request: Request, availability: Availability
    ) -> Response:
        """Return the availability of a service as an XML response."""
        return _templates.TemplateResponse(
            "availability.xml",
            {"availability": availability, "request": request},
            media_type="application/xml",
        )

    def error(self, request: Request, error: JobError) -> Response:
        """Return the error of a job as an XML response."""
        return _templates.TemplateResponse(
            "error.xml",
            {"error": error, "request": request},
            media_type="application/xml",
        )

    def job(self, request: Request, job: Job) -> Response:
        """Return a job as an XML response."""
        return _templates.TemplateResponse(
            "job.xml",
            {"job": job, "request": request},
            media_type="application/xml",
        )

    def job_list(
        self, request: Request, jobs: List[JobDescription], base_url: str
    ) -> Response:
        """Return a list of jobs as an XML response."""
        return _templates.TemplateResponse(
            "jobs.xml",
            {"base_url": base_url, "jobs": jobs, "request": request},
            media_type="application/xml",
        )

    def parameters(self, request: Request, job: Job) -> Response:
        """Return the parameters for a job as an XML response."""
        return _templates.TemplateResponse(
            "parameters.xml",
            {"job": job, "request": request},
            media_type="application/xml",
        )

    def results(self, request: Request, job: Job) -> Response:
        """Return the results for a job as an XML response."""
        return _templates.TemplateResponse(
            "results.xml",
            {"job": job, "request": request},
            media_type="application/xml",
        )
