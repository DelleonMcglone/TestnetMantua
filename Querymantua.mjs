// mantuaClient.mjs
// Minimal Mantua client (ESM) with optional context/session & chat streaming

// Ensure fetch exists (Node 18+ or a polyfill like undici)
if (typeof fetch !== 'function') {
    throw new Error('Global fetch is not available. Use Node 18+ or polyfill with undici.');
  }
  
  const API_BASE_URL =
    (typeof process !== "undefined" && process.env?.MANTUA_API_URL) ||
    "http://localhost:8000"; // your FastAPI server
  
  // ---- JSON fetch utility with basic error reporting
  async function apiRequest(endpoint, method, body = undefined, extraHeaders = {}) {
    const res = await fetch(`${API_BASE_URL}${endpoint}`, {
      method,
      headers: { "Content-Type": "application/json", ...extraHeaders },
      body: body ? JSON.stringify(body) : undefined,
    });
  
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
    }
    const ct = res.headers.get("content-type") || "";
    return ct.includes("application/json") ? res.json() : res.text();
  }
  
  /** ---------------------------
   * (Optional) Client-side session
   * ---------------------------
   * Mantua has no /session API yet; keep a stable local ID.
   */
  function getOrCreateLocalSessionId() {
    if (typeof window !== "undefined" && window.localStorage) {
      const key = "mantua_session_id";
      let id = window.localStorage.getItem(key);
      if (!id) {
        id =
          (typeof crypto !== "undefined" && crypto.randomUUID?.()) ||
          String(Date.now()) + Math.random().toString(36).slice(2);
        window.localStorage.setItem(key, id);
      }
      return id;
    }
    // Node fallback
    return (typeof crypto !== "undefined" && crypto.randomUUID?.()) ||
      String(Date.now()) + Math.random().toString(36).slice(2);
  }
  
  // ---------------------------
  // Streaming helper (fetch + SSE-style parsing)
  // ---------------------------
  /**
   * chatStream — POSTs to /chat with stream=true and invokes onEvent for each SSE "data:" line.
   * Options:
   *  - session_id?: string
   *  - context?: object
   *  - onEvent?: (data: any) => void
   */
  async function chatStream(message, { session_id, context, onEvent } = {}) {
    const res = await fetch(`${API_BASE_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, stream: true, session_id, context }),
    });
    if (!res.ok) {
      const text = await res.text().catch(() => "");
      throw new Error(`HTTP ${res.status} ${res.statusText}: ${text}`);
    }
    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buf = "";
  
    while (true) {
      const { value, done } = await reader.read();
      if (done) break;
      buf += decoder.decode(value, { stream: true });
  
      // Split SSE frames by double newline
      const frames = buf.split("\n\n");
      buf = frames.pop() || "";
  
      for (const frame of frames) {
        const line = frame.trim();
        if (!line.startsWith("data:")) continue;
        const payload = line.slice(5).trim();
        try {
          const obj = JSON.parse(payload);
          onEvent?.(obj);
        } catch {
          onEvent?.(payload);
        }
      }
    }
  }
  
  // ---------------------------
  // Mantua API wrappers
  // ---------------------------
  
  /**
   * chat — non-streaming chat call.
   * opts: { session_id?: string, context?: object, stream?: false }
   */
  async function chat(message, opts = {}) {
    const { session_id, context, stream = false } = opts;
    if (stream) {
      throw new Error("Use chatStream() for streaming responses.");
    }
    const payload = { message, stream: false, session_id, context };
    const data = await apiRequest("/chat", "POST", payload);
    return data?.response ?? data;
  }
  
  /**
   * simulate — dry-run evaluations.
   * opts: { session_id?: string, context?: object }
   */
  async function simulate(scenario, opts = {}) {
    const { session_id, context } = opts;
    return apiRequest("/simulate", "POST", { scenario, session_id, context });
  }
  
  /**
   * execute — live action (placeholder backend).
   * opts: { session_id?: string, context?: object, execute_config?: object }
   */
  async function execute(action, opts = {}) {
    const { session_id, context, execute_config } = opts;
    return apiRequest("/execute", "POST", { action, session_id, context, execute_config });
  }
  
  // ---------------------------
  // Convenience wrappers
  // ---------------------------
  
  async function createSession(title = "Mantua Session") {
    // Local-only session id for continuity
    return getOrCreateLocalSessionId();
  }
  
  /**
   * queryContract — uses /chat with a structured prompt (non-streaming).
   */
  async function queryContract(contractAddress, chainId, sessionId, extraContext = undefined) {
    const message = `
  Provide a concise, structured overview of the contract at ${contractAddress} on chain ${chainId}.
  Return strictly in this format:
  
  ### Contract Details:
  - **Name:** <contractName or "Unknown">
  - **Address:** ${contractAddress}
  - **Chain ID:** ${chainId}
  - **Blockchain:** <e.g., Base Sepolia>
  
  ### Read-only Functions:
  1. \`<fnName(params)>\`
     - **Returns:** <type>
     - **Description:** <what it does>
  
  ### Write-able Functions:
  1. \`<fnName(params)>\`
     - **Returns:** <type or "none">
     - **Description:** <what it does>
     - **Payable:** <true/false>
     - **Parameters:** <name> <type> <desc>
  
  If a section is empty, say "None available."
    `.trim();
  
    return chat(message, { session_id: sessionId, context: extraContext, stream: false });
  }
  
  /**
   * handleUserMessage — follow-up chat that threads lightweight context.
   */
  async function handleUserMessage(userMessage, sessionId, chainId, contractAddress, extraContext = undefined) {
    const message = `[context: chain=${chainId}, contract=${contractAddress}] ${userMessage}`;
    return chat(message, { session_id: sessionId, context: extraContext, stream: false });
  }
  
  /**
   * executeCommand — adapter to keep old Nebula-style call sites working.
   * Here we send only the 'action' string your server expects, plus context/config if provided.
   */
  async function executeCommand(
    message,
    signerWalletAddress,              // currently unused by server
    userId = "default-user",          // currently unused by server
    stream = false,                   // use chatStream for streaming chat, not execute
    chainId = undefined,              // optional, thread via context
    contractAddress = undefined,      // optional, thread via context
    sessionId = undefined,            // optional
    extra = {}                        // { context, execute_config }
  ) {
    const context = {
      ...(extra.context || {}),
      ...(chainId ? { chain_ids: [String(chainId)] } : {}),
      ...(contractAddress ? { contract_addresses: [contractAddress] } : {}),
    };
    return execute(message, { session_id: sessionId, context, execute_config: extra.execute_config });
  }
  
  export {
    // core
    chat,
    chatStream,
    simulate,
    execute,
    // helpers
    createSession,
    queryContract,
    handleUserMessage,
    executeCommand,
  };
  
