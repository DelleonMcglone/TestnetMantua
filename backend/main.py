"""FastAPI application exposing DEX assistant endpoints.

The backend provides three primary endpoints:

* `/query`    – parse natural language into a structured intent and return a summary.
* `/simulate` – perform a dry‑run of the requested transaction and return gas and output estimates.
* `/execute`  – (stub) execute the transaction on the blockchain and return a transaction hash.

Additional endpoints include `/health` for liveness probes and `/metrics` for future observability.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .errors import (
    IntentParsingError,
    RateLimitExceeded,
    SimulationError,
    ExecutionError,
)
from .intent_parser import parse_intent
from .models import (
    ExecutionRequest,
    ExecutionResponse,
    ExecutionResult,
    Intent,
    QueryRequest,
    QueryResponse,
    SimulationRequest,
    SimulationResponse,
)
from .simulation import simulate
from .tx_executor import execute_transaction
from .monitoring import setup_logging, get_health_router
from .hookrank_routes import router as hookrank_router
from .coingecko_routes import router as coingecko_router
from .auth import router as auth_router, get_current_user
from .database import init_db
from .rate_limiter import rate_limiter


app = FastAPI(title="Base DEX Assistant", version="0.1.0")

setup_logging(app)

# Allow cross‑origin requests from any domain (adjust in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database initialisation at startup
@app.on_event("startup")
def on_startup() -> None:
    """Initialise application resources."""
    init_db()


@app.post("/query", response_model=QueryResponse)
async def query(
    request_body: QueryRequest,
    request: Request,
    current_user: Any = Depends(get_current_user),
) -> QueryResponse:
    """Parse a natural language query into a structured intent and return it."""
    # Apply rate limiting
    rate_limiter(request)
    try:
        intent: Intent = parse_intent(request_body.prompt)
    except IntentParsingError as e:
        raise e
    # Compose a friendly message summarising the intent
    msg = f"Intent detected: {intent.action.value}. Parameters: {intent.parameters}"
    return QueryResponse(intent=intent, message=msg)


@app.post("/simulate", response_model=SimulationResponse)
async def simulate_endpoint(
    req: SimulationRequest,
    request: Request,
    current_user: Any = Depends(get_current_user),
) -> SimulationResponse:
    """Perform a dry‑run of the requested transaction."""
    rate_limiter(request)
    try:
        result = simulate(req.intent)
    except Exception as e:
        raise SimulationError(str(e))
    msg = "Simulation completed successfully"
    return SimulationResponse(result=result, message=msg)


@app.post("/execute", response_model=ExecutionResponse)
async def execute_endpoint(
    req: ExecutionRequest,
    request: Request,
    current_user: Any = Depends(get_current_user),
) -> ExecutionResponse:
    """Execute a transaction on chain.

    This stub implementation simply returns a fake transaction hash.  In
    production the logic would sign and send a transaction using the
    configured wallet or session key and return the real transaction hash.
    """
    rate_limiter(request)
    # Execute the transaction using the tx_executor module
    try:
        execution_result = execute_transaction(req.intent)
    except ExecutionError as e:
        # Propagate execution errors for FastAPI to handle
        raise e
    return ExecutionResponse(result=execution_result, message="Transaction submitted")


# Register health router
app.include_router(get_health_router())
app.include_router(hookrank_router)
app.include_router(coingecko_router)
app.include_router(auth_router)