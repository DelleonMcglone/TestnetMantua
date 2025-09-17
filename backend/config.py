"""Configuration handling for the backend service.

This module centralises the configuration of environment variables such as
API keys, RPC endpoints and feature flags.  Values are read from the
environment on import to avoid repeated lookups.  To modify the behaviour
of the application, set the corresponding environment variables before
starting the server.

Example:

```bash
export BASE_RPC_URL="https://base-mainnet.infura.io/v3/<your-api-key>"
export OPENAI_API_KEY="sk-..."
export COINGECKO_API_KEY="CG-LX..."
```
"""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""

    # Blockchain endpoints
    base_rpc_url: str = os.getenv("BASE_RPC_URL", "https://mainnet.base.org")
    base_sepolia_rpc_url: str = os.getenv(
        "BASE_SEPOLIA_RPC_URL", "https://sepolia.base.org"
    )

    # Uniswap v4 contract addresses (latest as of August 2025)
    # See: https://docs.uniswap.org/contracts/v4/deployments
    uniswap_v4_pool_manager_mainnet: str = os.getenv(
        "UNISWAP_V4_POOL_MANAGER_MAINNET", "0x498581ff718922c3f8e6a244956af099b2652b2b"
    )
    uniswap_v4_pool_manager_base: str = os.getenv(
        "UNISWAP_V4_POOL_MANAGER_BASE", "0x498581ff718922c3f8e6a244956af099b2652b2b"
    )
    uniswap_v4_pool_manager_base_sepolia: str = os.getenv(
        "UNISWAP_V4_POOL_MANAGER_BASE_SEPOLIA", "0x05E73354cFDd6745C338b50BcFDfA3Aa6fA03408"
    )

    # API keys
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    coingecko_api_key: Optional[str] = os.getenv("COINGECKO_API_KEY")

    # Model settings
    fine_tuned_model: str = os.getenv(
        "OPENAI_FINE_TUNED_MODEL", "ft:gpt-4-custom-intent-parser"
    )

    # Caching / rate limiting
    cache_ttl_seconds: int = int(os.getenv("CACHE_TTL_SECONDS", "60"))
    request_rate_limit_per_minute: int = int(
        os.getenv("REQUEST_RATE_LIMIT_PER_MINUTE", "60")
    )

    # Feature flags
    enable_intent_parser: bool = os.getenv("ENABLE_INTENT_PARSER", "true").lower()
    enable_simulation: bool = os.getenv("ENABLE_SIMULATION", "true").lower()
    enable_ml_models: bool = os.getenv("ENABLE_ML_MODELS", "true").lower()


settings = Settings()


__all__ = ["settings", "Settings"]