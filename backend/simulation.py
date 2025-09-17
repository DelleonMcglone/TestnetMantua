"""Transaction simulation engine.

This module provides functions to simulate actions on Uniswap v4 such
as swaps and liquidity additions.  Where possible it calls
on‑chain contracts or external price sources to compute realistic
estimates of expected output and gas usage.  In absence of live
on‑chain data, the implementation falls back to CoinGecko price
feeds to derive exchange rates.
"""

from typing import Any, Dict

import os
from typing import Any, Dict, Optional

import requests
from .models import Intent, SimulationResult
from .errors import SimulationError


# Mapping of common token symbols to CoinGecko API IDs.  This list
# can be extended as more tokens are supported.
_COINGECKO_IDS = {
    "ETH": "ethereum",
    "USDC": "usd-coin",
    "USDT": "tether",
    "BTC": "bitcoin",
    "cbBTC": "bitcoin",
    "WBTC": "wrapped-bitcoin",
    "DAI": "dai",
    "USDe": "usde",
}


def _fetch_token_price_usd(symbol: str) -> Optional[float]:
    """Fetch the current USD price for a token symbol via CoinGecko.

    Parameters
    ----------
    symbol: str
        Ticker symbol of the token (e.g. "ETH", "USDC").

    Returns
    -------
    float or None
        The token’s price in USD, or None if unavailable.
    """
    token_id = _COINGECKO_IDS.get(symbol.upper())
    if not token_id:
        return None
    try:
        resp = requests.get(
            "https://api.coingecko.com/api/v3/simple/price",
            params={"ids": token_id, "vs_currencies": "usd"},
            timeout=5,
        )
        data = resp.json()
        return float(data[token_id]["usd"])
    except Exception:
        return None


def simulate(intent: Intent) -> SimulationResult:
    """Simulate a transaction described by an Intent.

    This function produces estimates for gas usage, expected output and
    price impact based on the supplied intent.  For swaps it
    consults CoinGecko to obtain current token prices.  For adding
    liquidity it simply echoes the amounts provided.  Unknown actions
    raise a SimulationError.

    Parameters
    ----------
    intent: Intent
        Structured intent describing the desired action (e.g. swap 0.5 ETH for USDC).

    Returns
    -------
    SimulationResult
        Contains estimated gas, expected output and any additional details.

    Raises
    ------
    SimulationError
        If the intent action is unsupported or required parameters are missing.
    """
    action = intent.action.value
    details: Dict[str, Any] = {}
    if action == "swap":
        # Extract parameters
        try:
            amount_in = float(intent.parameters.get("amount"))
        except (TypeError, ValueError):
            raise SimulationError("Amount must be provided as a number")
        token_in = intent.parameters.get("token_in")
        token_out = intent.parameters.get("token_out")
        if not token_in or not token_out:
            raise SimulationError("token_in and token_out must be provided for swaps")
        # Fetch USD prices
        price_in = _fetch_token_price_usd(token_in)
        price_out = _fetch_token_price_usd(token_out)
        if price_in is None or price_out is None:
            raise SimulationError(f"Price data unavailable for {token_in} or {token_out}")
        # Compute output using price ratio and apply a 0.3% fee
        raw_output = amount_in * price_in / price_out
        expected_out_amount = raw_output * 0.997
        expected_output = f"{expected_out_amount:.6f} {token_out}"
        price_impact = 0.003  # placeholder for now
        details.update({"token_in": token_in, "token_out": token_out})
        gas_estimate = 150_000
    elif action == "add_liquidity":
        # Determine amounts of each token; default to symmetrical if only one provided
        amount_a = intent.parameters.get("amount_a")
        amount_b = intent.parameters.get("amount_b")
        try:
            amt_a = float(amount_a) if amount_a is not None else None
            amt_b = float(amount_b) if amount_b is not None else None
        except (TypeError, ValueError):
            raise SimulationError("Liquidity amounts must be numeric")
        # If only one amount given, replicate it for the second token
        if amt_a is None and amt_b is None:
            raise SimulationError("At least one of amount_a or amount_b must be provided")
        if amt_a is None:
            amt_a = amt_b
        if amt_b is None:
            amt_b = amt_a
        details.update({"amount_a": amt_a, "amount_b": amt_b})
        expected_output = "LP tokens minted"
        price_impact = None
        gas_estimate = 200_000
    elif action in {"execute", "query"}:
        # Forward to swap/liquidity simulation or return trivial result
        expected_output = "Execution simulated"
        price_impact = None
        gas_estimate = 180_000
    else:
        raise SimulationError(f"Unsupported action type: {action}")
    return SimulationResult(
        gas_estimate=gas_estimate,
        expected_output=expected_output,
        price_impact=price_impact,
        details=details,
    )