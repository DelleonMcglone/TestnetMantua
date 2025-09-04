from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, AsyncGenerator
import asyncio
import json
import os

# --- OpenAI (server-side) ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None  # handle missing dep gracefully

app = FastAPI()

# ---- CORS (dev-friendly) ----
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # tighten in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Config (env) ----
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "")  # e.g., ft:gpt-4o-mini:your-org:mantua-v1
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "")  # optional (Azure/compatible)

_client = None
if OpenAI and OPENAI_API_KEY:
    # If you use an alt endpoint, set base_url via env
    _client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL or None)

# ---- Models ----
class ContextFilters(BaseModel):
    chain_ids: Optional[List[str]] = None
    contract_addresses: Optional[List[str]] = None
    wallet_addresses: Optional[List[str]] = None
    token_addresses: Optional[List[str]] = None
    # extend as needed (protocols, pool_ids, metrics, etc.)

class ChatRequest(BaseModel):
    message: str
    stream: bool = False
    session_id: Optional[str] = None
    context: Optional[ContextFilters] = None

class SimulateRequest(BaseModel):
    scenario: str
    session_id: Optional[str] = None
    context: Optional[ContextFilters] = None

class ExecuteRequest(BaseModel):
    action: str
    session_id: Optional[str] = None
    context: Optional[ContextFilters] = None
    execute_config: Optional[dict] = None  # signer, mode, etc.

# ---- Helpers ----
def _chat_messages(user_message: str, context: Optional[ContextFilters], session_id: Optional[str]):
    sys_ctx = {
        "session_id": session_id,
        "context": (context.dict() if context else None),
        "policy": "Do not invent addresses. Respect provided chain_ids and contract_addresses."
    }
    system = (
        "You are Mantua's on-chain assistant. Use the provided context to ground answers. "
        "If data is missing, be explicit. Keep responses concise and action-oriented."
        f"\n<ctx>{json.dumps(sys_ctx)}</ctx>"
    )
    return [
        {"role": "system", "content": system},
        {"role": "user", "content": user_message},
    ]

async def _stream_openai_tokens(messages):
    """Yield SSE frames from OpenAI streaming."""
    if not _client or not OPENAI_MODEL:
        # Fallback: simple echo streaming
        chunks = ["[fallback-start]", " OpenAI not configured. ", "Echo: ", messages[-1]["content"], " [fallback-end]"]
        for c in chunks:
            yield f"data: {json.dumps({'type':'token','content': c})}\n\n".encode("utf-8")
            await asyncio.sleep(0.03)
        yield b"data: {\"type\":\"done\"}\n\n"
        return

    stream = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
        stream=True,
    )

    # optional: send a start event
    yield f"data: {json.dumps({'type':'start'})}\n\n".encode("utf-8")

    try:
        for event in stream:
            delta = event.choices[0].delta if event.choices else None
            token = getattr(delta, "content", None)
            if token:
                yield f"data: {json.dumps({'type':'token','content': token})}\n\n".encode("utf-8")
        # completed
        yield b"data: {\"type\":\"done\"}\n\n"
    except Exception as e:
        # surface an error event but keep SSE well-formed
        yield f"data: {json.dumps({'type':'error','message': str(e)})}\n\n".encode("utf-8")
        yield b"data: {\"type\":\"done\"}\n\n"

def _complete_openai(messages) -> str:
    """Return a full completion (no streaming)."""
    if not _client or not OPENAI_MODEL:
        return f"[fallback] OpenAI not configured. Echo: {messages[-1]['content']}"
    resp = _client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return (resp.choices[0].message.content or "").strip()

# ---- Endpoints ----
@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """
    Natural language chat: proxies to OpenAI (server-side) or falls back.
    stream=True -> SSE; otherwise -> JSON.
    """
    messages = _chat_messages(request.message, request.context, request.session_id)

    if request.stream:
        async def event_generator() -> AsyncGenerator[bytes, None]:
            # Context ack (optional)
            ack = {
                "type": "context_ack",
                "session_id": request.session_id,
                "context": (request.context.dict() if request.context else None),
                "model": OPENAI_MODEL or "fallback",
            }
            yield f"data: {json.dumps(ack)}\n\n".encode("utf-8")
            async for frame in _stream_openai_tokens(messages):
                yield frame
        return StreamingResponse(event_generator(), media_type="text/event-stream")

    # Non-streaming
    content = _complete_openai(messages)
    return {
        "response": content,
        "session_id": request.session_id,
        "context": (request.context.dict() if request.context else None),
        "model": OPENAI_MODEL or "fallback",
    }

@app.post("/simulate")
async def simulate_endpoint(request: SimulateRequest):
    """Evaluate a scenario without touching the blockchain (placeholder)."""
    return {
        "simulation": f"Simulated scenario: {request.scenario}",
        "session_id": request.session_id,
        "context": (request.context.dict() if request.context else None),
    }

@app.post("/execute")
async def execute_endpoint(request: ExecuteRequest):
    """Trigger a blockchain action (placeholder for now)."""
    return {
        "status": f"Executed action: {request.action}",
        "session_id": request.session_id,
        "context": (request.context.dict() if request.context else None),
        "execute_config": request.execute_config,
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
