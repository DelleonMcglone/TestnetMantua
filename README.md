# TestnetMantua

# 🚀 Mantua Protocol

Mantua Protocol is a blockchain-native large language model (LLM) purpose-built for programmable liquidity on the Base blockchain. Mantua enables LPs, traders, and Uniswap hook developers to manage liquidity pools, swaps, and advanced DeFi strategies — all through a conversational AI chat interface.

Mantua goes beyond generic DeFi bots by offering real-time onchain data, advanced smart contract reasoning, and autonomous transaction execution. Our goal is to replace complex dashboards with an AI-native user experience, making decentralized finance accessible and programmable for everyone.

---

## ✨ Key Features
✅ Conversational AI interface for swaps, bridging, liquidity, and Uniswap v4 hooks  
✅ Real-time blockchain data fetching from Base mainnet & Sepolia testnet  
✅ Autonomous transaction execution with session key management  
✅ Support for Uniswap v4 programmable hooks  
✅ Inline swap & liquidity UI components  
✅ API endpoints for integrating external agents and tools  
✅ SPA (single-page app) frontend with wallet connection & confirmation flows  
✅ Light/dark mode with mobile-responsive design  
✅ Self-hosted LLM for privacy, low latency, and full control

---

## 🛠️ Tech Stack
- LLM: [Mistral 7B](https://mistral.ai/) (fine-tuned on smart contracts, transactions, Uniswap hooks)
- Inference: Ollama (testing) → vLLM (production)
- Frontend: Next.js + Tailwind CSS
- Backend: FastAPI (REST/WebSocket)
- Blockchain: Base RPC, Uniswap v4 SDK
- Wallets: wagmi, thirdweb/onchainkit
- CI/CD: GitHub Actions
- Hosting: Vercel/Netlify (SPA) + GPU server for LLM/API

---

## ⚙️ Architecture Overview
- **Frontend SPA**: Runs on Vercel/Netlify → connects to API server → hosts chat interface.
- **API Server**: FastAPI → integrates with LLM (Ollama/vLLM) → connects to Base RPC → executes transactions.
- **Blockchain Integration**: Direct read/wri
