"""Logging, monitoring and health checks.

This module centralises the configuration of structured logging and exposes a
FastAPI dependency for request logging.  It also defines a `/health` endpoint
that can be used by load balancers and monitoring systems to verify that
the service is up and responsive.
"""

import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, FastAPI, Request

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("dex-assistant")


def setup_logging(app: FastAPI) -> None:
    """Attach middleware to log incoming requests and responses."""

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        logger.info(
            "Request: %s %s from %s", request.method, request.url.path, request.client.host
        )
        start_time = datetime.utcnow()
        response = await call_next(request)
        duration = (datetime.utcnow() - start_time).total_seconds()
        logger.info(
            "Response: %s %s status=%d duration=%.3fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response


def get_health_router() -> APIRouter:
    """Return a router with a simple health check endpoint."""

    router = APIRouter()

    @router.get("/health", summary="Health check endpoint")
    async def health() -> dict:
        return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

    return router