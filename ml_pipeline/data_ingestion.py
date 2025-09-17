"""Data ingestion for the ML pipeline.

This module provides functions for collecting price volatility data,
liquidity flows and LP positions across multiple timeframes and pools.  It
supports both on‑chain and off‑chain sources such as CoinGecko, Dexscreener
and custom RPC calls.  All functions return `pandas` DataFrames ready for
further processing.

Notes
-----
* **CoinGecko API** – used for historical price and volume data.  See
  <https://docs.coingecko.com/reference/mcp-server> for details.  Use
  `COINGECKO_API_KEY` from `backend/config.py` if available.
* **Dexscreener API** – provides live token pairs, charts and volume.  See
  <https://dexscreener.com/api/> for documentation.
* **Uniswap v4 SDK or on‑chain RPC** – required to fetch LP positions and
  liquidity flows from specific pools.  These calls are placeholders in
  this version.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional

import httpx
import pandas as pd

from ..backend.config import settings


COINGECKO_API_BASE = "https://api.coingecko.com/api/v3"
DEXSCREENER_API_BASE = "https://api.dexscreener.com/latest"


@dataclass
class PriceData:
    timestamp: datetime
    price: float
    volume: float


def fetch_price_history(
    token_id: str,
    days: int = 30,
    interval: str = "hourly",
) -> pd.DataFrame:
    """Fetch historical price and volume data for a token from CoinGecko.

    Parameters
    ----------
    token_id: str
        The CoinGecko identifier for the token (e.g. ``ethereum`` or ``usd-coin``).
    days: int
        Number of days of history to retrieve.
    interval: str
        Data granularity (``daily`` or ``hourly``).  Hourly intervals provide
        more granularity but are limited to 90 days on CoinGecko.

    Returns
    -------
    pd.DataFrame
        DataFrame with columns ``timestamp``, ``price`` and ``volume``.
    """
    api_key = settings.coingecko_api_key
    params = {
        "vs_currency": "usd",
        "days": days,
        "interval": interval,
    }
    headers = {}
    if api_key:
        headers["x-cg-pro-api-key"] = api_key
    url = f"{COINGECKO_API_BASE}/coins/{token_id}/market_chart"
    resp = httpx.get(url, params=params, headers=headers, timeout=20.0)
    resp.raise_for_status()
    data = resp.json()
    prices = data.get("prices", [])
    volumes = data.get("total_volumes", [])
    rows: List[PriceData] = []
    for (ts, price), (_, volume) in zip(prices, volumes):
        rows.append(PriceData(timestamp=datetime.fromtimestamp(ts / 1000), price=price, volume=volume))
    df = pd.DataFrame(rows)
    return df


def fetch_pool_liquidity_history(
    pool_address: str,
    chain: str = "base",
    lookback_hours: int = 24,
) -> pd.DataFrame:
    """Fetch liquidity flow data for a given pool from Dexscreener.

    Dexscreener exposes an endpoint for historical aggregated data.  At the
    moment the public API is limited; this function uses a placeholder
    implementation returning an empty DataFrame.  Extend it by calling
    Dexscreener once the endpoint is open.

    Parameters
    ----------
    pool_address: str
        Address of the liquidity pool.
    chain: str
        Chain identifier used by Dexscreener (e.g. ``ethereum``, ``base``).
    lookback_hours: int
        Number of hours of history to retrieve.

    Returns
    -------
    pd.DataFrame
        DataFrame with time‑indexed liquidity and volume metrics.
    """
    # TODO: implement real call to Dexscreener once API is stable
    now = datetime.utcnow()
    timestamps = [now - timedelta(hours=i) for i in range(lookback_hours, -1, -1)]
    df = pd.DataFrame({
        "timestamp": timestamps,
        "liquidity": [0.0] * (lookback_hours + 1),
        "volume": [0.0] * (lookback_hours + 1),
    })
    return df


def fetch_lp_positions_v4(pool_manager: str, address: str) -> pd.DataFrame:
    """Retrieve LP positions for a given address on Uniswap v4.

    This stub returns an empty DataFrame.  When implemented, it should
    query the pool manager contract on the specified chain and return
    details such as token amounts, liquidity range and fees earned.

    Parameters
    ----------
    pool_manager: str
        Address of the Uniswap v4 pool manager contract (see deployments in docs).
    address: str
        LP provider address to query.

    Returns
    -------
    pd.DataFrame
        DataFrame enumerating positions and their parameters.
    """
    # TODO: integrate with v4 SDK or on‑chain calls
    return pd.DataFrame(columns=["token0", "token1", "amount0", "amount1", "fees"])