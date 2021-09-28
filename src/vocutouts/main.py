"""The main application factory for the vo-cutouts service.

Notes
-----
Be aware that, following the normal pattern for FastAPI services, the app is
constructed when this module is loaded and is not deferred until a function is
called.
"""

from importlib.metadata import metadata

import structlog
from fastapi import FastAPI
from safir.dependencies.http_client import http_client_dependency
from safir.logging import configure_logging
from safir.middleware.x_forwarded import XForwardedMiddleware

from .config import config
from .handlers.external import external_router
from .handlers.internal import internal_router
from .policy import ImageCutoutPolicy
from .uws.dependencies import uws_dependency
from .uws.errors import install_error_handlers
from .uws.middleware import CaseInsensitiveQueryMiddleware
from .worker import task

__all__ = ["app", "config"]


configure_logging(
    profile=config.profile,
    log_level=config.log_level,
    name=config.logger_name,
)

app = FastAPI()
"""The main FastAPI application for vo-cutouts."""

# Define the external routes in a subapp so that it will serve its own OpenAPI
# interface definition and documentation URLs under the external URL.
_subapp = FastAPI(
    title="vo-cutouts",
    description=metadata("vo-cutouts").get("Summary", ""),
    version=metadata("vo-cutouts").get("Version", "0.0.0"),
)
_subapp.include_router(
    external_router, responses={401: {"description": "Unauthenticated"}}
)

# Attach the internal routes and subapp to the main application.
app.include_router(internal_router)
app.mount(f"/{config.name}", _subapp)


@app.on_event("startup")
async def startup_event() -> None:
    app.add_middleware(XForwardedMiddleware)
    app.add_middleware(CaseInsensitiveQueryMiddleware)
    logger = structlog.get_logger(config.logger_name)
    install_error_handlers(app)
    install_error_handlers(_subapp)
    await uws_dependency.initialize(
        config=config.uws_config(),
        actor=task,
        policy=ImageCutoutPolicy(),
        logger=logger,
    )


@app.on_event("shutdown")
async def shutdown_event() -> None:
    await http_client_dependency.aclose()
