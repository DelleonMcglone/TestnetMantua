from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import AsyncGenerator
import asyncio

app = FastAPI()

class ChatRequest(BaseModel):
    """Request model for natural language chat interactions."""
    message: str
    stream: bool = False

class SimulateRequest(BaseModel):
    """Request model for scenario simulation."""
    scenario: str

class ExecuteRequest(BaseModel):
    """Request model for on-chain action execution."""
    action: str

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Handle natural language interactions with the AI.

    Returns a streaming response via Server-Sent Events (SSE) when
    ``stream`` is ``True``. Otherwise, a standard JSON payload is
    returned once processing completes.
    """

    # Placeholder logic for chat processing
    if request.stream:
        async def event_generator() -> AsyncGenerator[bytes, None]:
            for word in ["Streaming", "response:", request.message]:
                yield f"data: {word}\n\n".encode("utf-8")
                await asyncio.sleep(0.1)

        return StreamingResponse(event_generator(), media_type="text/event-stream")

    return {"response": f"Received message: {request.message}"}

@app.post("/simulate")
async def simulate_endpoint(request: SimulateRequest):
    """Evaluate a scenario without touching the blockchain."""
    # Placeholder logic for simulation
    return {"simulation": f"Simulated scenario: {request.scenario}"}

@app.post("/execute")
async def execute_endpoint(request: ExecuteRequest):
    """Trigger a blockchain action without relying on conversation history."""
    # Placeholder logic for execution
    return {"status": f"Executed action: {request.action}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
