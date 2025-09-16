# Mantua.AI – AI-Native DeFi Agent on Base

An AI-powered on-chain assistant that connects natural language to blockchain actions. Built on **Base** with **Uniswap v4 hooks**, autonomous agents, and real-time blockchain reasoning.

## Project Structure

```text
Mantua.AI/
├── backend/             # FastAPI backend with /query, /simulate, /execute endpoints
│   ├── main.py          # Entrypoint
│   ├── intent_parser.py # AI intent → structured actions
│   ├── simulation.py    # Swap/liquidity simulation engine
│   ├── tx_executor.py   # Transaction execution logic
│   └── models.py        # Pydantic request/response models
├── ml_pipeline/         # Data + model training pipeline
│   ├── data_ingestion.py
│   ├── feature_engineering.py
│   └── model_training.py
├── hooks/               # Example Uniswap v4 Solidity hooks
│   ├── DynamicFeeHook.sol
│   └── LiquidityProtectionHook.sol
├── datasets/            # Sample datasets (testing/demo only)
│   └── samples/
│       ├── cbbtc_price_vol_sample.csv
│       ├── ethereum_price_vol_sample.csv
│       └── eurc_price_vol_sample.csv
├── tests/               # Unit tests for backend modules
│   ├── test_coingecko_endpoints.py
│   ├── test_hookrank_endpoints.py
│   ├── test_simulation.py
│   └── test_tx_executor.py
└── frontend/            # Next.js + Tailwind UI (WIP)
```

## Getting Started

### Backend
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend (placeholder)
```bash
cd frontend
npm install
npm run dev
```

### Datasets
- Sample CSVs live under `datasets/samples/`.
- Use them for dev/testing (not production).

## Core Features

- **Natural Language to Onchain Actions** — Convert chat requests into structured transactions.
- **Simulation Engine** — Back-test swaps and liquidity moves before executing them on-chain.
- **Autonomous Agents** — Spin up bots with user-defined risk and parameters to handle trades and yield strategies.
- **Hooks Integration** — Support Uniswap v4 dynamic fee, MEV protection, liquidity optimization hooks, etc.

## Development & Testing

Run unit tests with:

```bash
pytest tests/
```

These tests cover:

- CoinGecko & HookRank endpoints
- Swap and liquidity simulation engine
- Transaction executor

## Disclaimer

Smart contracts and hooks in this repository are experimental and unaudited. Use only in test environments. This project is for research and educational purposes; there is no warranty.
