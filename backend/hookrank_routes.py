"""FastAPI router exposing HookRank API proxy endpoints.

This module defines an APIRouter that mirrors a subset of the HookRank
public API.  It leverages the :class:`HookRankClient` to perform
HTTP requests and returns the results in a consistent JSON format.
Clients of this API should prefer these endpoints over calling
HookRank directly so that the backend can handle caching, error
handling and future authentication in one place.

Example usage:

    from fastapi import FastAPI
    from .hookrank_routes import router as hookrank_router

    app = FastAPI()
    app.include_router(hookrank_router)

"""

from __future__ import annotations

from typing import Optional, Dict, Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .hookrank_client import HookRankClient, HookRankAPIError

router = APIRouter(prefix="/hookrank", tags=["hookrank"])

# Create a singleton client for reuse across requests.  The base URL
# for the HookRank API can be overridden via the HOOKRANK_API_BASE
# environment variable.
_client = HookRankClient()


@router.get("/networks")
async def list_networks() -> JSONResponse:
    """List networks with available hooks.

    Returns a JSON object containing a ``data`` key whose value is
    the list of networks.  On error, returns a 502 Bad Gateway with
    an ``error`` key.
    """
    try:
        networks = _client.get_networks()
        return JSONResponse(content={"data": networks})
    except HookRankAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@router.get("/currencies")
async def list_currencies() -> JSONResponse:
    """List currencies supported by HookRank."""
    try:
        currencies = _client.get_currencies()
        return JSONResponse(content={"data": currencies})
    except HookRankAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@router.get("/hooks")
async def list_hooks(
    network: Optional[str] = None,
    currency: Optional[str] = None,
    page: Optional[int] = None,
    limit: Optional[int] = None,
) -> JSONResponse:
    """List hooks with optional filtering and pagination.

    Parameters are passed through to the upstream HookRank API if
    provided.  Unknown parameters are ignored.  The response
    contains a ``data`` key with the list of hooks.
    """
    params: Dict[str, Any] = {}
    if network:
        params["network"] = network
    if currency:
        params["currency"] = currency
    if page is not None:
        params["page"] = page
    if limit is not None:
        params["limit"] = limit
    try:
        hooks = _client.get_hooks(params=params or None)
        return JSONResponse(content={"data": hooks})
    except HookRankAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@router.get("/hooks/{chain_id}/{hook_address}")
async def get_hook(chain_id: int, hook_address: str) -> JSONResponse:
    """Fetch information about a specific hook.

    The ``chain_id`` and ``hook_address`` identify the hook.  The
    response includes a ``data`` key with the hook metadata.
    """
    try:
        hook = _client.get_hook(chain_id, hook_address)
        return JSONResponse(content={"data": hook})
    except HookRankAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@router.get("/hooks/{chain_id}/{hook_address}/contract-metadata")
async def get_hook_contract_metadata(chain_id: int, hook_address: str) -> JSONResponse:
    """Fetch contract metadata for a specific hook.

    Returns ABI and deployment information for the hook contract.
    """
    try:
        metadata = _client.get_hook_contract_metadata(chain_id, hook_address)
        return JSONResponse(content={"data": metadata})
    except HookRankAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})