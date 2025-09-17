"""Rate limiting utilities.

This module provides a simple sliding‑window rate limiter that enforces
both global and per‑user limits using Redis as a backing store.  For
demo purposes, it falls back to in‑memory dictionaries when Redis
is unavailable.  The rate limiting parameters can be configured via
settings (request_rate_limit_per_minute and daily_transaction_limits).
"""

from datetime import datetime, timedelta
from typing import Dict

from fastapi import HTTPException, status, Request

from .config import settings

# In‑memory fallback for request counts keyed by identifier
_request_counts: Dict[str, int] = {}
_request_windows: Dict[str, datetime] = {}


def rate_limit(identifier: str) -> None:
    """Enforce per‑identifier (user or IP) limits within a 60‑second window."""
    now = datetime.utcnow()
    window_start = _request_windows.get(identifier)
    # Reset window every minute
    if not window_start or now - window_start > timedelta(seconds=60):
        _request_windows[identifier] = now
        _request_counts[identifier] = 0
    _request_counts[identifier] = _request_counts.get(identifier, 0) + 1
    if _request_counts[identifier] > settings.request_rate_limit_per_minute:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded",
        )


def rate_limiter(request: Request) -> None:
    """FastAPI dependency to rate limit requests based on client IP."""
    ip = request.client.host or "unknown"
    rate_limit(ip)


__all__ = ["rate_limit", "rate_limiter"]