"""Model training and management for the ML pipeline.

This module contains functions and classes to train, evaluate and version
machine‑learning models used by the DEX assistant.  The primary use cases
include:

* **Volatility prediction models** – forecast short‑term market volatility to
  adjust fees or recommend LP strategies.
* **Liquidity optimisation models** – infer optimal liquidity placement
  within a Uniswap v4 pool given current market conditions.
* **Dynamic fee models** – compute fee multipliers based on volatility and
  predicted user flow.

Model artefacts should be stored in a persistent storage bucket (e.g. S3,
GCS) and versioned using a naming scheme or MLflow.  GPU acceleration
through PyTorch is supported but optional.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
import torch
import torch.nn as nn
import torch.optim as optim


@dataclass
class ModelMetadata:
    name: str
    version: str
    metrics: Dict[str, float]
    path: str


def train_linear_volatility_model(features: pd.DataFrame, target_column: str) -> Tuple[LinearRegression, ModelMetadata]:
    """Train a simple linear regression model to predict volatility.

    Parameters
    ----------
    features: pd.DataFrame
        DataFrame containing engineered features.  Should include the
        `target_column` representing the future volatility to predict.
    target_column: str
        Name of the column in `features` that holds the target variable.

    Returns
    -------
    model: LinearRegression
        Trained linear regression model.
    metadata: ModelMetadata
        Metadata containing model information and training metrics.
    """
    # Prepare input matrices
    X = features.drop(columns=[target_column]).values
    y = features[target_column].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled, y, test_size=0.2, random_state=42
    )
    model = LinearRegression()
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    mse = mean_squared_error(y_test, preds)
    metadata = ModelMetadata(
        name="linear_volatility_model",
        version="1.0.0",
        metrics={"mse": mse},
        path="linear_volatility_model.pkl",
    )
    # Persist model and scaler
    import joblib  # type: ignore

    joblib.dump({"model": model, "scaler": scaler}, metadata.path)
    return model, metadata


class NeuralFeeModel(nn.Module):
    """Simple feed‑forward network for dynamic fee prediction."""

    def __init__(self, input_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 1),
            nn.Sigmoid(),  # output between 0 and 1 for fee multiplier
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:  # type: ignore
        return self.net(x)


def train_fee_model(features: pd.DataFrame, target: pd.Series, epochs: int = 50) -> Tuple[nn.Module, ModelMetadata]:
    """Train a neural network to predict fee multipliers.

    Parameters
    ----------
    features: pd.DataFrame
        Input features for training.
    target: pd.Series
        Target values (e.g. optimal fee multipliers between 0 and 1).
    epochs: int
        Number of training epochs.

    Returns
    -------
    model: nn.Module
        Trained neural network model.
    metadata: ModelMetadata
        Metadata containing metrics and file path.
    """
    X = torch.tensor(features.values, dtype=torch.float32)
    y = torch.tensor(target.values, dtype=torch.float32).unsqueeze(1)
    model = NeuralFeeModel(input_dim=X.shape[1])
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)
    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()
        outputs = model(X)
        loss = criterion(outputs, y)
        loss.backward()
        optimizer.step()
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch+1}/{epochs}, Loss: {loss.item():.6f}")
    # Compute final MSE
    model.eval()
    with torch.no_grad():
        final_preds = model(X)
        final_mse = criterion(final_preds, y).item()
    metadata = ModelMetadata(
        name="neural_fee_model",
        version="1.0.0",
        metrics={"mse": final_mse},
        path="neural_fee_model.pt",
    )
    torch.save(model.state_dict(), metadata.path)
    return model, metadata