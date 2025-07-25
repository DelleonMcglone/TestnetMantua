# Unified Hooks Index for Mantua Protocol

This directory contains data files and contract outlines for the Mantua Protocol's
research into Uniswap v4 hooks and infrastructure on the Base Sepolia network,
OpenZeppelin’s Uniswap Hook Suite, and popular hooks deployed on the Base
network as catalogued by HookRank.  The aim of this index is to provide a
machine‑readable collection of contract addresses, descriptions and meta‑data
that can be used to fine tune large language models to reason about, monitor
and interact with Uniswap liquidity pools and custom hooks.

The structure is as follows:

- **`unified_index.csv`** – a CSV file summarising all entries across the
  different sources.  Each row contains the following fields: `category`,
  `name`, `contract_address`, `network`, `description` and `notes`.
- **`base_sepolia_contracts.csv`** – specific contract addresses for Uniswap v4
  infrastructure on the Base Sepolia testnet, pulled from Uniswap’s official
  deployment documentation.
- **`hookrank_base_hooks.csv`** – contract addresses and on‑chain metrics for a
  selection of hooks deployed on the Base network and indexed by HookRank.
  These hooks were filtered to include only those on Base and the most active
  ones available at the time of research.  Each row includes the hook name,
  address, deployed timestamp, number of pools, swaps, trading volume, TVL,
  success rate, total fees and protocol fees.

These resources can be extended by appending additional rows to the CSV files
when new hooks or networks become relevant.
