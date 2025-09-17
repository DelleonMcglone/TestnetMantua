"""Uniswap v4 client helper.

This module wraps interactions with Uniswap v4 via Web3.py.  It
initialises a Web3 client against the Base Sepolia network and
provides helper functions for querying pools and verifying
connectivity.  Real liquidity management and pool interactions should
be implemented here in future iterations.
"""

from typing import Any, Optional
import os

from web3 import Web3
from web3.middleware import geth_poa_middleware

from .config import settings


def get_web3() -> Web3:
    """Return a Web3 client configured for Base Sepolia or mainnet."""
    rpc_url = settings.base_sepolia_rpc_url or settings.base_rpc_url
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def check_indexer() -> bool:
    """Verify connectivity to the Uniswap v4 pool manager contract.

    Returns True if the contract code is non‑empty, False otherwise.
    """
    w3 = get_web3()
    pool_manager_address = settings.uniswap_v4_pool_manager_base_sepolia
    code = w3.eth.get_code(pool_manager_address)
    return len(code) > 0


__all__ = ["get_web3", "check_indexer"]