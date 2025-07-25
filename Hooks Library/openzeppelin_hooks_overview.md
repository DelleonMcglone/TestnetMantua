# OpenZeppelin Uniswap Hooks Overview

OpenZeppelin maintains a suite of hooks built on top of the Uniswap v4 hook
interface.  These are Solidity contracts intended to be inherited and
deployed as part of custom hook logic; they are **not** deployed on chain by
default, so there are no fixed contract addresses.  Below is a summary of
the three ready‑to‑use hooks provided by the suite along with a link to the
raw Solidity source and a brief description of their purpose and behaviour.

| Hook | Description | Source Link |
|-----|-------------|------------|
| **LiquidityPenaltyHook** | A just‑in‑time (JIT) liquidity provisioning resistant hook.  It disincentivizes JIT attacks by **penalising liquidity providers** who add liquidity and immediately remove it to collect fees.  During `afterAddLiquidity` the hook withholds fee accrual if liquidity was added recently, and during `afterRemoveLiquidity` it applies a penalty on recently added positions and donates the penalty fees to the in‑range LPs【902492714642474†L36-L55】.  If an LP adds liquidity continuously they must wait for a `blockNumberOffset` before removing to avoid the penalty.  Functions exposed include `getBlockNumberOffset()`, `getLastAddedLiquidityBlock()`, `getWithheldFees()` and internal methods for calculating the penalty【902492714642474†L74-L90】. | [`LiquidityPenaltyHook.sol`](https://github.com/OpenZeppelin/uniswap-hooks/blob/master/src/general/LiquidityPenaltyHook.sol) |
| **AntiSandwichHook** | Implements a **sandwich‑resistant AMM design**.  During `_beforeSwap` it records the pool state at the beginning of each block and ensures that swaps within the same block cannot receive better prices than those available at the start of the block.  This protects against sandwich attacks on swaps, but only for swaps in the `!zeroForOne` direction【902492714642474†L275-L299】.  Developers inheriting this hook must implement `_handleCollectedFees` to decide what to do with fees collected by the anti‑sandwich mechanism.  Available functions include `_beforeSwap`, `_getTargetUnspecified`, `_afterSwapHandler` and `getHookPermissions()`【902492714642474†L302-L336】. | [`AntiSandwichHook.sol`](https://github.com/OpenZeppelin/uniswap-hooks/blob/master/src/general/AntiSandwichHook.sol) |
| **LimitOrderHook** | Provides an on‑chain **limit order mechanism** for Uniswap v4 pools.  Users can place a limit order by supplying liquidity at a target tick outside of the current price range.  When the price crosses the specified tick the order is filled; otherwise users can cancel or add more liquidity at any time.  When an order is cancelled or topped up, any accrued fees are added to the order info for the remaining limit order holders【902492714642474†L448-L468】.  Key functions include `placeOrder`, `cancelOrder`, `withdraw`, `_afterInitialize` and `_afterSwap`【902492714642474†L476-L507】. | [`LimitOrderHook.sol`](https://github.com/OpenZeppelin/uniswap-hooks/blob/master/src/general/LimitOrderHook.sol) |

## Notes

* The hooks described above are part of OpenZeppelin’s Uniswap Hooks library and can be inherited and customised as needed.  They rely on Uniswap v4’s hook entry points such as `beforeSwap`, `afterSwap`, `beforeAddLiquidity`, `afterAddLiquidity` and others.  The library is **experimental**; developers should use it with caution and review its suitability for production.
* Since these hooks are not deployed by default, there are **no fixed contract addresses**.  To use them in practice, you must compile and deploy them with your desired parameters and integrate them with your own PoolManager.
