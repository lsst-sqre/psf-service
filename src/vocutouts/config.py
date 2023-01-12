"""Configuration definition."""

from __future__ import annotations

import os
from dataclasses import dataclass

from .uws.config import UWSConfig

__all__ = ["Configuration", "config"]


@dataclass
class Configuration:
    """Configuration for vocutouts."""

    storage_url: str = os.getenv("CUTOUT_STORAGE_URL", "")
    """The root URL to use to store cutout results.

    This must be an ``s3`` URL pointing to a Google Cloud Storage bucket that
    is writable by the backend and readable by the frontend.
    """

    database_url: str = os.getenv("CUTOUT_DATABASE_URL", "")
    """The URL for the UWS job database.

    Set with the ``CUTOUT_DATABASE_URL`` environment variable.  Setting this
    is mandatory.
    """

    database_password: str | None = os.getenv("CUTOUT_DATABASE_PASSWORD")
    """The password for the UWS job database.

    Set with the ``CUTOUT_DATABASE_PASSWORD`` environment variable.
    """

    signing_service_account: str = os.getenv("CUTOUT_SERVICE_ACCOUNT", "")
    """Email of service account to use for signed URLs.

    The default credentials that the application frontend runs with must have
    the ``roles/iam.serviceAccountTokenCreator`` role on the service account
    with this email.
    """

    execution_duration: int = int(os.getenv("CUTOUT_TIMEOUT", "600"))
    """The timeout for a single cutout job.

    Set with the ``CUTOUT_TIMEOUT`` environment variable.  The default is
    10 minutes.
    """

    lifetime: int = int(os.getenv("CUTOUT_LIFETIME", str(7 * 24 * 60 * 60)))
    """The lifetime for which job results will be retained.

    Set with the ``CUTOUT_LIFETIME`` environment variable.  The default is
    seven days.
    """

    redis_host: str = os.getenv("CUTOUT_REDIS_HOST", "")
    """Hostname of the Redis server used by Dramatiq.

    Set with the ``CUTOUT_REDIS_HOST`` environment variable.  Setting this is
    mandatory.
    """

    redis_password: str | None = os.getenv("CUTOUT_REDIS_PASSWORD")
    """Password for the Redis server used by Dramatiq.

    Set with the ``CUTOUT_REDIS_PASSWORD`` environment variable.
    """

    sync_timeout: int = int(os.getenv("CUTOUT_SYNC_TIMEOUT", "60"))
    """The timeout for results from a sync cutout.

    Set with the ``CUTOUT_SYNC_TIMEOUT`` environment variable.  The default is
    one minute.
    """

    tmpdir: str = os.getenv("CUTOUT_TMPDIR", "/tmp")
    """Temporary directory to use for cutouts before uploading them to GCS."""

    name: str = os.getenv("SAFIR_NAME", "cutout")
    """The application's name, which doubles as the root HTTP endpoint path.

    Set with the ``SAFIR_NAME`` environment variable.
    """

    profile: str = os.getenv("SAFIR_PROFILE", "development")
    """Application run profile: "development" or "production".

    Set with the ``SAFIR_PROFILE`` environment variable.
    """

    logger_name: str = os.getenv("SAFIR_LOGGER", "vocutouts")
    """The root name of the application's logger.

    Set with the ``SAFIR_LOGGER`` environment variable.
    """

    log_level: str = os.getenv("SAFIR_LOG_LEVEL", "INFO")
    """The log level of the application's logger.

    Set with the ``SAFIR_LOG_LEVEL`` environment variable.
    """

    def uws_config(self) -> UWSConfig:
        """Convert to configuration for the UWS subsystem."""
        return UWSConfig(
            execution_duration=self.execution_duration,
            lifetime=self.lifetime,
            database_url=self.database_url,
            database_password=self.database_password,
            redis_host=self.redis_host,
            redis_password=self.redis_password,
            signing_service_account=self.signing_service_account,
        )


config = Configuration()
"""Configuration for vo-cutouts."""
