"""Client for the HookRank public API.

This module provides a thin wrapper around the HookRank API for
discovering Uniswap v4 hooks.  The base URL can be configured via
the `HOOKRANK_API_BASE` environment variable.  Each method returns
JSON decoded into Python data structures and raises
`HookRankAPIError` on HTTP errors.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

import httpx


class HookRankAPIError(Exception):
    """Raised when the HookRank API returns an error or is unreachable."""

    pass


class HookRankClient:
    """Client for interacting with the HookRank public API.

    The client exposes methods corresponding to documented endpoints:

    - `get_networks` – list networks with hook activity.
    - `get_currencies` – list supported currencies across networks.
    - `get_hooks` – list all hooks with optional filters.
    - `get_hook` – fetch metadata for a single hook by chain ID and address.
    - `get_hook_contract_metadata` – fetch contract metadata for a single hook.

    All methods return the JSON payload as a Python object.  Errors
    such as non‑200 responses or connection failures raise
    `HookRankAPIError`.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: float = 10.0) -> None:
        self.base_url = base_url or os.getenv(
            "HOOKRANK_API_BASE", "https://hookrank.io/api/public/v1/uniswap/hooks"
        )
        self.timeout = timeout
        self.client = httpx.Client(timeout=self.timeout)

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{path}"
        try:
            resp = self.client.get(url, params=params)
            resp.raise_for_status()
            return resp.json()
        except Exception as exc:
            raise HookRankAPIError(f"HookRank API request failed: {exc}")

    def get_networks(self) -> List[Dict[str, Any]]:
        """Return a list of networks with available hooks."""
        data = self._get("/networks")
        return data.get("data", data)

    def get_currencies(self) -> List[Dict[str, Any]]:
        """Return a list of currencies supported by HookRank."""
        data = self._get("/currencies")
        return data.get("data", data)

    def get_hooks(self, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Return a list of hooks.

        Parameters can include filters such as `network`, `currency` or
        pagination options (e.g. `page`, `limit`).
        """
        data = self._get("", params=params)
        return data.get("data", data)

    def get_hook(self, chain_id: int, hook_address: str) -> Dict[str, Any]:
        """Return information about a specific hook by chain ID and address."""
        data = self._get(f"/{chain_id}/{hook_address}")
        return data.get("data", data)

    def get_hook_contract_metadata(self, chain_id: int, hook_address: str) -> Dict[str, Any]:
        """Return contract metadata for a specific hook."""
        data = self._get(f"/{chain_id}/{hook_address}/contract-metadata")
        return data.get("data", data)


__all__ = ["HookRankClient", "HookRankAPIError"]