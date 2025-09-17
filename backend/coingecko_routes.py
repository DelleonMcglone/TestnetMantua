"""FastAPI router exposing CoinGecko API proxy endpoints.

This router provides a thin proxy over a subset of the CoinGecko
public API.  It allows clients to fetch current prices, coin
metadata and trending coins through the DEX assistant backend.  The
underlying :class:`CoinGeckoClient` handles HTTP calls and API key
injection.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from .coingecko_client import CoinGeckoClient, CoinGeckoAPIError

router = APIRouter(prefix="/coingecko", tags=["coingecko"])

_client = CoinGeckoClient()


@router.get("/price")
async def get_price(
    ids: str,
    vs_currencies: str,
    include_market_cap: Optional[bool] = False,
    include_24hr_vol: Optional[bool] = False,
    include_24hr_change: Optional[bool] = False,
) -> JSONResponse:
    """Fetch simple price data for one or more coins.

    Query parameters correspond to the CoinGecko ``/simple/price`` API.
    At minimum, ``ids`` and ``vs_currencies`` must be provided as
    comma-separated strings.  Optional flags can be toggled to
    include additional data.
    """
    try:
        prices = _client.get_simple_price(
            ids,
            vs_currencies,
            include_market_cap=bool(include_market_cap),
            include_24hr_vol=bool(include_24hr_vol),
            include_24hr_change=bool(include_24hr_change),
        )
        return JSONResponse(content={"data": prices})
    except CoinGeckoAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@router.get("/coin/{coin_id}")
async def get_coin(coin_id: str) -> JSONResponse:
    """Return detailed information about a single coin."""
    try:
        coin = _client.get_coin_info(coin_id)
        return JSONResponse(content={"data": coin})
    except CoinGeckoAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})


@router.get("/trending")
async def get_trending() -> JSONResponse:
    """Return trending coins as ranked by CoinGecko."""
    try:
        trending = _client.get_trending()
        return JSONResponse(content={"data": trending})
    except CoinGeckoAPIError as exc:
        return JSONResponse(status_code=502, content={"error": str(exc)})