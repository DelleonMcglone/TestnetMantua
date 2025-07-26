# Mantua Hook Library Index

This document provides a high‑level overview of the hooks and contract
addresses collected for the Mantua Protocol and explains how to use the
included index to answer questions such as **“What are the trending hooks
for Swaps ETH/USDe?”**.  It also outlines how to fetch and decode
transaction logs via the Blockscout (BaseScan) API and how Tenderly can be
used to simulate transactions and obtain revert reasons.  The goal is
to equip Mantua’s LLM with the contextual knowledge needed to reason
about Uniswap v4 pools, custom hooks and on‑chain activity.

## Categories in the index

The unified index groups entries into several categories:

| Category       | Description |
|---------------|------------|
| **BaseSepolia** | Core Uniswap v4 contracts deployed on the Base Sepolia testnet (PoolManager, UniversalRouter, PositionManager, etc.).  These addresses are needed for interacting with the protocol and for decoding logs. |
| **HookRankBase** | Verified hooks deployed on the Base network and catalogued by HookRank.  Each entry includes the hook name, address, deployment date, number of pools, swaps, trading volume, total value locked (TVL), success rate and fee metrics. |
| **UniswapExample** | Non‑deployed example hooks from Uniswap’s quick‑start documentation.  These examples (`SwapHook`, `LiquidityHook`, `AsyncSwapHook`) illustrate how to implement hooks for swaps, liquidity operations and asynchronous swaps【930650411521099†L63-L78】【987634694816832†L63-L79】. |

The OpenZeppelin hook summaries have been removed at the user’s request.  If you wish to include them again, the source files remain in the repository but are not referenced here.

## Trending hooks (Base network)

To identify “trending” hooks, we use the trading volume metric from the
HookRank data.  The following table lists the top hooks by lifetime
trading volume on the Base network.  These hooks can be used when
answering queries about high‑activity swaps, including pairs like
ETH/USDe.  Note that HookRank does not currently provide pair‑specific
statistics, so the ranking below is based on overall volume and
activity.

| Hook name | Address | Pools | Swaps | Trading volume | TVL | Success rate | Purpose/notes |
|----------|--------|------|------|----------------|-----|--------------|---------------|
| **Flaunch** | `0x51bba15255406cfe7099a42183302640ba7dafdc` | 4 730 | 239 891 | ≈$95.35 M | ≈$5.15 M | 100 % | High‑activity hook enabling large numbers of pools and swaps on Base【129814954585930†screenshot】. |
| **VerifiedPoolsBasicHook** | `0x5cd525c621afca515bf58631d37d3bfa7b72aae4` | 5 | 31 136 | ≈$5.91 M | ≈$1.85 M | 100 % | Ensures pools meet verification requirements before trades are executed【157990363365919†screenshot】. |
| **SpawnerHook** | `0xb476c448da4453208df4e371fee26f4e630d3044` | 14 959 | 29 040 | ≈$4.30 M | ≈$135 199 | 100 % | Creates new pools or positions, often used for farming and dynamic liquidity【919161640951837†screenshot】. |
| **LimitOrderHook (HookRank)** | `0x9d119f505ca92f4b6983c1285d1ac0aaf7ec0c0` | 6 | 45 932 | ≈$2.40 M | ≈$80 228 | 100 % | Provides on‑chain limit orders for Uniswap v4 pools【919161640951837†screenshot】. |
| **PositionManager (HookRank)** | `0x7f85bb58059fbaf6bf19bdd2b9078d9e546efdc` | 2 442 | 9 237 | ≈$1.18 M | ≈$182 104 | 100 % | Helps manage positions across pools on Base【807146418858899†screenshot】. |
| **Politiswap** | `0x4cd3be87688aea2a0297c22c17a73cae65adc0cc` | 537 | 2 957 | ≈$0.98 M | ≈$454 430 | 100 % | Swap‑centric hook focusing on political‑themed liquidity pools【309274945707880†screenshot】. |
| **ContentmentHook** | `0x2a0e6206325c966fee8b2284ca1a276877332844` | 1 | 944 | ≈$0.57 M | ≈$25 448 | 100 % | Niche hook with low volume; emphasises “contentment” liquidity strategies【919161640951837†screenshot】. |
| **BtcAccHook** | `0x70426ac7043aeef50f47b6a03ae68ccf808e044` | 7 | 1 512 | ≈$0.55 M | ≈$31 204 | 100 % | Small hook that accumulates BTC and executes occasional swaps【919161640951837†screenshot】. |

When the LLM is asked “What are the trending hooks for Swaps ETH/USDe?”, it
should refer to this table and return the most active hooks for the Base
network along with their usage metrics.  For example, **Flaunch** has the
highest trading volume and swap count, so it would be flagged as the
top candidate.  Each hook entry in the unified index also records its
source—`HookRankBase` for these examples—so the LLM can explain whether
data comes from Uniswap’s official deployments or third‑party analytics.

## Fetching transaction logs via Blockscout (BaseScan)

Uniswap v4 events are emitted by the `PoolManager` contract.  The
important events for hook analysis include:

* **Initialize** — emitted when a new pool is created【332502846784097†L168-L176】.
* **ModifyLiquidity** — emitted before the `afterModifyLiquidity` hook is called【332502846784097†L211-L215】.
* **Swap** — emitted before the `afterSwap` hook is called and includes swap fee information【332502846784097†L293-L304】.

To retrieve logs for a specific hook or pool, you can use the
Blockscout API (used by BaseScan) without an API key.  The endpoint
structure is:

```
https://base.blockscout.com/api?module=logs&action=getLogs&fromBlock=<startBlock>&toBlock=<endBlock>&address=<contractAddress>&topic0=<eventTopic>
```

Where:

* `address` is the contract you want to monitor (e.g., the hook or
  `PoolManager` address).
* `topic0` is the keccak‑256 hash of the event signature (for example,
  `Swap(address,address,int256,int256,uint160,uint128,int24,uint24)` for the
  `Swap` event).  If you omit `topic0`, all logs from the contract will
  be returned.
* `fromBlock`/`toBlock` define the block range.  Use `0` and
  `latest` to scan the entire chain.  Note that the API limits the
  result to 1 000 logs per call; for large ranges, you should paginate.

Example: to fetch all `Swap` events for the **Flaunch** hook over the
entire chain:

```
https://base.blockscout.com/api?module=logs&action=getLogs&fromBlock=0&toBlock=latest&address=0x51bba15255406cfe7099a42183302640ba7dafdc
```

You will receive a JSON array of log objects.  Each log contains
`topics` and `data` fields; decode these using the Uniswap v4 ABI to
extract parameters such as the pool ID, currencies, amounts, swap
fee, etc.  The `topics[0]` entry corresponds to the event signature
hash.

## Simulating transactions and capturing failures with Tenderly

Tenderly’s simulation API allows you to execute a transaction off‑chain
to observe its effects and capture revert reasons.  This is useful for
training the LLM on edge cases where swaps or liquidity modifications
fail.  To use Tenderly:

1. Sign up for a Tenderly account and obtain an API key.
2. Use the `simulate-transaction` endpoint to run a call against the
   Base network.  Provide the `to` address (usually the `PoolManager`),
   calldata for the function (e.g., `swap`), and optional state
   overrides.
3. Inspect the response’s `transaction_status` and `error_message`
   fields.  Failed simulations will include a revert reason and the
   stack trace.  Successful simulations return decoded logs similar to
   on‑chain receipts.

By combining Blockscout logs for real transactions with Tenderly
simulations, you can build a comprehensive dataset of both successful
and failed operations, ensuring the LLM can reason about typical and
edge‑case behaviours.

## How to use this index programmatically

The unified index is stored as CSV files.  To query them via Python
for example:

```python
import pandas as pd

# load unified index
df = pd.read_csv('unified_index.csv')

# filter to HookRankBase and sort by trading volume (converted to a number)
def parse_volume(val):
    s = str(val).replace('_','').replace('$','').replace(',','').strip()
    if s.endswith('M'):  # millions
        return float(s[:-1]) * 1e6
    if s.endswith('K'):  # thousands
        return float(s[:-1]) * 1e3
    return float(s or 0)

df_hookrank = df[df['category'] == 'HookRankBase'].copy()
df_hookrank['volume_num'] = df_hookrank['trading_volume'].apply(parse_volume)
top = df_hookrank.sort_values('volume_num', ascending=False).head(3)
print(top[['name','contract_address','trading_volume']])
```

This snippet loads the index, extracts Base hooks and sorts them by
trading volume.  You can adapt it to filter by token pair (once
pair‑specific metrics are available), volume threshold, or hook
category (e.g., MEV protection, dynamic fee, rewards) to power your
Mantua‑native queries.

## Data structure (for fine‑tune readiness)

The Mantua dataset is structured to facilitate model fine‑tuning.  Each record
includes the hook name, address, category, source, trading metrics and
descriptive metadata.  You can load the CSV into a DataFrame and convert
it to the format expected by your training pipeline (e.g., JSONL with
fields like `instruction`, `input`, `output`).

### Critical additions

To ensure the model only learns from valid contracts, add a validation
layer that cross‑checks each address against official Uniswap
deployments and the verified Base hooks list.

```python
# Cross‑check hook and core contracts against official Uniswap deployments and verified Base hooks
UNISWAP_CORE = load_uniswap_official_addresses()
VERIFIED_HOOKS = load_hookrank_verified_hooks()

def validate_contract(address: str) -> bool:
    """Return True if the address is either an official Uniswap core address or a verified hook."""
    return address.lower() in UNISWAP_CORE or address.lower() in VERIFIED_HOOKS
```

### Synthetic data plan

If real on‑chain data is sparse for certain hooks or edge cases, you can
generate synthetic training examples using simulation tools such as
Foundry.  Simulate swaps and liquidity operations with and without
hooks, including scenarios that revert due to MEV protection, custom
fees or limit‑order triggers.  Export the simulated traces to
`/llm/train.jsonl` for training.
