# psf-service

psf-service is a [FastAPI](https://fastapi.tiangolo.com/) web service and associated backend worker implementation that implements a PSF-recreation and visualization-support service for the Rubin Science Platform.
The underlying work of generating the PSF representation as an image, for a specified point, is delegated to [lsst.psf_service_backend](https://github.com/lsst-dm/psf_service_backend/).

Based on the design of the Rubin Science Platform SODA service, vo-cutouts.
