"""Client for the CoinGecko public API.

This module provides a small wrapper around selected CoinGecko API
endpoints.  It supports optional API keys (for pro/demo tiers) via
the ``COINGECKO_API_KEY`` environment variable.  Each method
returns the JSON payload from CoinGecko, or raises a
:class:`CoinGeckoAPIError` on failure.  See the official
documentation for details on available endpoints and parameters.
"""

from __future__ import annotations

import os
from typing import Any, Dict, Optional

import httpx


class CoinGeckoAPIError(Exception):
    """Raised when a call to the CoinGecko API fails."""

    pass


class CoinGeckoClient:
    """Client for interacting with the CoinGecko public API.

    The client exposes a few convenience methods for common endpoints:

    - ``get_simple_price`` – fetch the current price for one or more coins.
    - ``get_coin_info`` – return detailed metadata for a single coin.
    - ``get_trending`` – list trending coins as ranked by CoinGecko.

    Additional endpoints can be added as needed by using the
    underlying ``_get`` helper.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout: float = 10.0,
    ) -> None:
        self.base_url = base_url or os.getenv("COINGECKO_API_BASE", "https://api.coingecko.com/api/v3")
        # API key can be provided via environment variable or passed directly
        self.api_key = api_key or os.getenv("COINGECKO_API_KEY")
        self.client = httpx.Client(timeout=timeout)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        headers: Dict[str, str] = {}
        if self.api_key:
            # According to CoinGecko docs, supply API key via header
            # See: https://docs.coingecko.com/v3.0.1/reference/authentication
            headers["x-cg-demo-api-key"] = self.api_key
        try:
            resp = self.client.get(url, params=params, headers=headers)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise CoinGeckoAPIError(f"CoinGecko API request failed: {exc}")

    def get_simple_price(
        self,
        ids: str,
        vs_currencies: str,
        include_market_cap: bool = False,
        include_24hr_vol: bool = False,
        include_24hr_change: bool = False,
    ) -> Dict[str, Any]:
        """Retrieve the current price of one or more coins.

        Args:
            ids: comma-separated list of CoinGecko IDs (e.g. 'bitcoin,ethereum').
            vs_currencies: comma-separated list of target currencies (e.g. 'usd,eth').
            include_market_cap: include market cap data if True.
            include_24hr_vol: include 24h volume data if True.
            include_24hr_change: include 24h price change if True.

        Returns:
            A mapping from coin ID to pricing information.
        """
        params = {
            "ids": ids,
            "vs_currencies": vs_currencies,
        }
        if include_market_cap:
            params["include_market_cap"] = "true"
        if include_24hr_vol:
            params["include_24hr_vol"] = "true"
        if include_24hr_change:
            params["include_24hr_change"] = "true"
        return self._get("/simple/price", params=params)

    def get_coin_info(self, coin_id: str) -> Dict[str, Any]:
        """Fetch detailed information for a given coin.

        Args:
            coin_id: the CoinGecko ID of the coin (e.g. 'bitcoin').

        Returns:
            A nested dict containing coin metadata, market data and community data.
        """
        return self._get(f"/coins/{coin_id}")

    def get_trending(self) -> Dict[str, Any]:
        """Return a list of trending coins as defined by CoinGecko."""
        return self._get("/search/trending")


__all__ = ["CoinGeckoClient", "CoinGeckoAPIError"]