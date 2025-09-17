"""Pydantic models used by the FastAPI routes.

Having strict schemas for incoming requests and outgoing responses makes
the API self‑documenting and easier to integrate.  These models cover
basic request types such as queries, simulations and execution commands.
"""

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class ActionType(str, Enum):
    """Enumeration of supported action types returned by the intent parser."""

    QUERY = "query"
    SWAP = "swap"
    ADD_LIQUIDITY = "add_liquidity"
    EXECUTE = "execute"
    CUSTOM = "custom"


class QueryRequest(BaseModel):
    """Body model for the `/query` endpoint."""

    prompt: str = Field(
        ..., description="Natural language question or command provided by the user"
    )


class Intent(BaseModel):
    """Structured representation of an intent parsed from user input."""

    action: ActionType
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameters required to fulfil the intent"
    )
    confidence: float = Field(
        0.0,
        description="Confidence score between 0 and 1 indicating how certain the parser is",
    )


class QueryResponse(BaseModel):
    """Response model for the `/query` endpoint."""

    intent: Intent
    message: str


class SimulationRequest(BaseModel):
    """Body model for the `/simulate` endpoint."""

    intent: Intent


class SimulationResult(BaseModel):
    """Result returned from a transaction simulation."""

    gas_estimate: int
    expected_output: Optional[str]
    price_impact: Optional[float]
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional simulation information"
    )


class SimulationResponse(BaseModel):
    """Response model for the `/simulate` endpoint."""

    result: SimulationResult
    message: str


class ExecutionRequest(BaseModel):
    """Body model for the `/execute` endpoint."""

    intent: Intent
    simulation_id: Optional[str] = Field(
        None,
        description="Identifier linking to a previous simulation; optional if the client opted out of simulation",
    )


class ExecutionResult(BaseModel):
    """Result returned from executing a transaction."""

    tx_hash: str
    explorer_url: Optional[str]
    status: str
    details: Dict[str, Any] = Field(
        default_factory=dict, description="Additional execution information"
    )


class ExecutionResponse(BaseModel):
    """Response model for the `/execute` endpoint."""

    result: ExecutionResult
    message: str