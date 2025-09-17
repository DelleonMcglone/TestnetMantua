"""Feature engineering utilities for the ML pipeline.

This module contains functions that transform raw data (price histories,
liquidity flows, user behaviours) into numerical features suitable for
machine‑learning models.  Feature engineering is critical for building
accurate volatility predictors and fee optimisation algorithms.

Examples of features:
* Rolling standard deviation and variance of prices and volumes.
* Liquidity imbalance between token pairs.
* User trade frequency and average trade size.
"""

from __future__ import annotations

import pandas as pd


def compute_volatility_features(price_df: pd.DataFrame, window: int = 24) -> pd.DataFrame:
    """Compute rolling volatility features for a price DataFrame.

    Parameters
    ----------
    price_df: pd.DataFrame
        DataFrame returned by `data_ingestion.fetch_price_history` with
        ``timestamp``, ``price`` and ``volume`` columns.
    window: int
        Window size (in periods) over which to compute rolling statistics.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with additional columns ``return``, ``volatility``,
        and ``rolling_volume``.
    """
    df = price_df.copy().sort_values("timestamp")
    # Percentage return between successive prices
    df["return"] = df["price"].pct_change().fillna(0)
    # Rolling standard deviation of returns
    df["volatility"] = df["return"].rolling(window=window).std().fillna(0)
    # Rolling sum of volume as a liquidity proxy
    df["rolling_volume"] = df["volume"].rolling(window=window).sum().fillna(0)
    return df


def compute_liquidity_features(liquidity_df: pd.DataFrame, window: int = 24) -> pd.DataFrame:
    """Compute features from liquidity flow data.

    Parameters
    ----------
    liquidity_df: pd.DataFrame
        DataFrame returned by `data_ingestion.fetch_pool_liquidity_history` with
        ``timestamp``, ``liquidity`` and ``volume`` columns.
    window: int
        Window size (in periods) over which to compute rolling statistics.

    Returns
    -------
    pd.DataFrame
        Original DataFrame with additional columns capturing liquidity trends.
    """
    df = liquidity_df.copy().sort_values("timestamp")
    df["liquidity_change"] = df["liquidity"].diff().fillna(0)
    df["volume_change"] = df["volume"].diff().fillna(0)
    df["liquidity_volatility"] = df["liquidity_change"].rolling(window=window).std().fillna(0)
    return df


def compute_user_behavior_features(trade_history: pd.DataFrame) -> pd.DataFrame:
    """Compute user behaviour features from trade history.

    Parameters
    ----------
    trade_history: pd.DataFrame
        A DataFrame with at least columns ``timestamp``, ``amount`` and
        ``token`` representing user trades.

    Returns
    -------
    pd.DataFrame
        User‑level aggregate statistics such as trade frequency and average size.
    """
    # Group by user if present; assume trade_history contains a 'user' column
    if "user" in trade_history.columns:
        grouped = trade_history.groupby("user")
    else:
        trade_history = trade_history.assign(user="anonymous")
        grouped = trade_history.groupby("user")
    features = grouped.agg(
        trade_count=("amount", "count"),
        avg_trade_size=("amount", "mean"),
        total_volume=("amount", "sum"),
    ).reset_index()
    return features