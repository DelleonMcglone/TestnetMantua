"""Transaction execution logic for the Base network.

This module encapsulates all logic required to sign and broadcast
transactions to the Base network using Web3.py.  It is separated
from the FastAPI route definitions to aid testing and reuse.  The
current implementation sends a no‑op transaction (zero value transfer
to the signer’s own address) as a placeholder.  Future versions
should replace this with calls to Uniswap v4 pools or other smart
contracts.

Functions defined here must raise `ExecutionError` on failure and
return an `ExecutionResult` on success.  All configuration is
read from environment variables via the Settings class in
`config.py`.
"""

from __future__ import annotations

import os
from typing import Optional

from web3 import Web3, exceptions as web3_exceptions
from web3.middleware import geth_poa_middleware

from .config import settings
from .models import Intent, ExecutionResult
from .errors import ExecutionError


def _get_web3_client(rpc_url: str) -> Web3:
    """Initialise and return a Web3 client for the given RPC URL.

    Parameters
    ----------
    rpc_url: str
        The JSON‑RPC endpoint for the Base network (e.g. Sepolia).

    Returns
    -------
    Web3
        Configured Web3 instance with middleware applied.
    """
    w3 = Web3(Web3.HTTPProvider(rpc_url))
    # Base Sepolia uses a proof‑of‑authority consensus; inject the POA middleware
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    if not w3.is_connected():
        raise ExecutionError("Unable to connect to RPC endpoint")
    return w3


def _build_placeholder_tx(w3: Web3, from_address: str) -> dict:
    """Construct a simple zero‑value transaction.

    This helper builds a transaction that sends zero ETH to the sender’s
    own address.  It serves as a placeholder until real pool calls
    are implemented.

    Parameters
    ----------
    w3: Web3
        The Web3 client used to query network information.
    from_address: str
        The address from which the transaction originates.

    Returns
    -------
    dict
        A dictionary representing the transaction object ready for
        signing.
    """
    nonce = w3.eth.get_transaction_count(from_address)
    gas_price = w3.eth.gas_price
    tx = {
        "nonce": nonce,
        "to": from_address,
        "value": 0,
        "gas": 21_000,
        "gasPrice": gas_price,
        # Chain ID 84532 corresponds to Base Sepolia; default to mainnet
        "chainId": int(os.getenv("CHAIN_ID", "84532")),
    }
    return tx


def execute_transaction(intent: Intent) -> ExecutionResult:
    """Sign and submit a transaction based on the provided intent.

    Currently this function ignores the intent parameters and sends a
    placeholder transaction.  Future enhancements should derive the
    transaction’s destination, data and value from `intent.parameters`.

    Parameters
    ----------
    intent: Intent
        The structured intent describing the desired action.

    Returns
    -------
    ExecutionResult
        Result object containing the transaction hash, explorer URL and
        execution status.

    Raises
    ------
    ExecutionError
        If the RPC connection fails, the private key is missing or
        signing/submission encounters an error.
    """
    # Choose the appropriate RPC URL; default to Base Sepolia for testing
    rpc_url: str = settings.base_sepolia_rpc_url or settings.base_rpc_url
    # Retrieve private key from environment
    private_key: Optional[str] = os.getenv("PRIVATE_KEY")
    if not private_key:
        raise ExecutionError("Private key not provided in environment")
    try:
        w3 = _get_web3_client(rpc_url)
    except ExecutionError:
        # Reraise connection errors as ExecutionError
        raise
    # Derive account from private key
    try:
        account = w3.eth.account.from_key(private_key)
    except ValueError as exc:
        raise ExecutionError(f"Invalid private key: {exc}")
    # Build transaction
    tx_dict = _build_placeholder_tx(w3, account.address)
    # Sign
    try:
        signed_tx = account.sign_transaction(tx_dict)
    except Exception as exc:  # broad catch to surface any signing error
        raise ExecutionError(f"Failed to sign transaction: {exc}")
    # Send
    try:
        tx_hash_bytes = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
    except web3_exceptions.TransactionNotFound as exc:
        # Rare: if transaction is not recognised after sending
        raise ExecutionError(f"Transaction not found after submission: {exc}")
    except Exception as exc:
        # Catch other Web3 errors (e.g. insufficient funds)
        raise ExecutionError(f"Failed to send transaction: {exc}")
    tx_hash = tx_hash_bytes.hex()
    explorer_url = f"https://sepolia.basescan.org/tx/{tx_hash}" if rpc_url == settings.base_sepolia_rpc_url else f"https://basescan.org/tx/{tx_hash}"
    return ExecutionResult(
        tx_hash=tx_hash, explorer_url=explorer_url, status="pending", details={}
    )


__all__ = ["execute_transaction"]