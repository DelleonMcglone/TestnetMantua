"""
Mantua Prompt Templates
=======================

This module defines a class containing static methods for generating natural‑language
prompts for interacting with the Mantua Protocol.  Each method returns a
dictionary with a `template` string, a description of the required fields,
and a list of example prompts illustrating common usage patterns.  The
templates are based on the Mantua whitepaper and fine‑tuning data, and
incorporate optional conditions such as MEV protection, dynamic fee hooks,
and TWAMM hooks【172126337518783†L61-L115】.  To customise a prompt,
substitute the bracketed placeholders with concrete values and, where
appropriate, add or remove optional lines.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class PromptDefinition:
    """Container for a prompt template and associated examples."""

    template: str
    fields: Dict[str, str]
    examples: List[str] = field(default_factory=list)


class MantuaPromptTemplates:
    """Collection of static methods returning prompt definitions for Mantua interactions."""

    @staticmethod
    def swap() -> PromptDefinition:
        """
        Build a swap prompt definition.

        Returns:
            PromptDefinition: Contains the template string, field descriptions
            and example prompts including dynamic fee hooks and hook names.
        """
        template = (
            "Swap {amount} {from_token} for {to_token} with a maximum slippage of {slippage}%\n"
            "{optional_conditions}\n"
            "{execution_preference}"
        )
        fields = {
            "amount": "Quantity of the source token (e.g., '50').",
            "from_token": "Token being sold (e.g., 'ETH').",
            "to_token": "Token being purchased (e.g., 'USDC').",
            "slippage": "Maximum slippage percentage tolerated for the swap.",
            "optional_conditions": (
                "(Optional) Additional triggers such as 'when gas < 25 gwei',\n"
                "'only if price < $2,000', 'use a dynamic fee hook', or\n"
                "'use the {hook_name} hook'."
            ),
            "execution_preference": "(Optional) e.g., 'Show me the execution plan before proceeding'.",
        }
        examples = [
            # Basic swap with gas condition
            "Swap 50 ETH for USDC with a maximum slippage of 1%. Execute when gas < 30 gwei. Show me the execution plan before proceeding.",
            # Swap using a dynamic fee hook
            "Swap 100 USDC to ETH using a dynamic fee hook and limit slippage to 0.5%. Execute only if gas < 25 gwei.",
            # Swap specifying a hook by name
            "Swap 200 DAI to WBTC using the ArrakisDynamicFee hook. Maximum slippage 0.3%. Show me the execution plan."
        ]
        return PromptDefinition(template=template, fields=fields, examples=examples)

    @staticmethod
    def liquidity_provision() -> PromptDefinition:
        """
        Build a liquidity provision (LP) prompt definition.

        Returns:
            PromptDefinition: Contains the template string, field descriptions
            and example prompts including MEV protection and TWAMM usage.
        """
        template = (
            "Add liquidity to the {token0}/{token1} pool with {amount0} {token0} and {amount1} {token1},\n"
            "targeting a price range of {lower_price}–{upper_price}.\n"
            "Set a stop-loss at {stop_loss}% and auto-compound LP rewards when gas fees are below {gas_threshold} gwei.\n"
            "{optional_strategy}\n"
            "{execution_preference}"
        )
        fields = {
            "token0/token1": "The two tokens in the pool (e.g., 'ETH', 'USDC').",
            "amount0/amount1": "Amounts to deposit.",
            "lower_price/upper_price": "Price range for concentrated liquidity.",
            "stop_loss": "Percentage loss at which to remove liquidity.",
            "gas_threshold": "Gas price (in gwei) below which auto-compounding should run.",
            "optional_strategy": (
                "(Optional) Additional management rules such as 'rebalance my position when volatility exceeds 15%'\n"
                "or 'use MEV protection' or 'use the {hook_name} hook'."
            ),
            "execution_preference": "(Optional) Ask to see the execution plan."
        }
        examples = [
            # Example from documentation
            (
                "Add liquidity to the ETH/USDC pool with 10 ETH and 30,000 USDC, targeting a price range of $1,800–$2,200.\n"
                "Set a stop-loss at 5% and auto-compound LP rewards when gas fees are below 20 gwei.\n"
                "Rebalance my position when volatility exceeds 15%.\n"
                "Show me the execution plan before proceeding."
            ),
            # MEV protection example
            (
                "Add liquidity to the WETH/USDC pool with 5 WETH and 18,000 USDC at a price range of $1,700–$2,100.\n"
                "Use MEV protection and auto-compound rewards when gas < 25 gwei."
            ),
            # TWAMM hook example
            (
                "Provide liquidity to the ETH/USDC pool with 3 ETH and 9,000 USDC using the TWAMM hook.\n"
                "Set a stop-loss at 4% and enable auto-compounding."
            )
        ]
        return PromptDefinition(template=template, fields=fields, examples=examples)

    @staticmethod
    def bridge() -> PromptDefinition:
        """
        Build a bridge prompt definition.

        Returns:
            PromptDefinition: Contains the template string, field descriptions
            and example prompts including commonly used bridging commands.
        """
        template = (
            "Bridge {amount} {token} from {source_chain} to {target_chain} with a maximum slippage of {slippage}%.\n"
            "{time_or_fee_condition}\n"
            "{execution_preference}"
        )
        fields = {
            "amount": "Number of tokens to bridge.",
            "token": "Token symbol (e.g., 'USDC').",
            "source_chain": "Origin chain (e.g., 'Base').",
            "target_chain": "Destination chain (e.g., 'Ethereum', 'Arbitrum').",
            "slippage": "Slippage tolerance percentage.",
            "time_or_fee_condition": "(Optional) Execution trigger, such as 'execute when gas < 20 gwei' or 'execute after 08:00 UTC'.",
            "execution_preference": "(Optional) Ask for execution plan."
        }
        examples = [
            # Base to Ethereum example
            "Bridge 1,000 USDC from Base to Ethereum with a maximum slippage of 0.3%. Execute when gas < 25 gwei. Show me the execution plan before proceeding.",
            # Simple bridging example from external reference
            "Bridge 100 USDC from Arbitrum to EduChain."
        ]
        return PromptDefinition(template=template, fields=fields, examples=examples)

    @staticmethod
    def hook_deployment() -> PromptDefinition:
        """
        Build a hook deployment prompt definition.

        Returns:
            PromptDefinition: Contains the template string, field descriptions
            and example prompts for deploying TWAMM and dynamic fee hooks.
        """
        template = (
            "Create a custom hook for the {token0}/{token1} pool that implements {hook_functionality}.\n"
            "Set parameters: {parameters}.\n"
            "{automation_conditions}\n"
            "{execution_preference}"
        )
        fields = {
            "token0/token1": "Tokens in the pool.",
            "hook_functionality": (
                "Description of the hook’s purpose, e.g., 'dynamic fee based on volatility',\n"
                "'auto-compound LP rewards', 'MEV protection' or 'TWAMM'."
            ),
            "parameters": "Key variables (e.g., base_fee = 0.3%, volatility_threshold = 10%, compounding_interval = 1 hour).",
            "automation_conditions": "(Optional) Conditions for the hook’s actions, such as 'when gas < 20 gwei' or 'when volatility exceeds 15%'.",
            "execution_preference": "(Optional) Ask for the execution plan."
        }
        examples = [
            # TWAMM hook deployment
            (
                "Use the TWAMM hook for the ETH/USDC pool. Set parameters: sell_amount = 1,000 tokens per second, duration = 7 days.\n"
                "Rebalance when volatility drops below 5%. Show me the execution plan."
            ),
            # Dynamic fee hook deployment
            (
                "Deploy a dynamic fee hook on the WETH/USDC pool.\n"
                "Set base_fee = 0.25%, volatility_threshold = 8%, max_fee = 0.8%.\n"
                "Auto-compound rewards when gas < 20 gwei."
            ),
        ]
        return PromptDefinition(template=template, fields=fields, examples=examples)

    @staticmethod
    def contract_analysis() -> PromptDefinition:
        """
        Build a contract analysis prompt definition.

        Returns:
            PromptDefinition: Contains the template string, field descriptions
            and example prompts for analysing hooks, pools, and combinations.
        """
        template = (
            "Analyse the following contract:\n"
            "``"\n"
            "{contract_code}\n"
            "``"\n"
            "Please:\n"
            "1. Summarise the key functions and their purposes.\n"
            "2. Identify any Uniswap v4 hook interactions or external calls.\n"
            "3. Highlight potential security risks or gas inefficiencies.\n"
            "4. Explain how this contract could be used for {use_case}.\n"
            "5. Suggest improvements or tests if necessary."
        )
        fields = {
            "contract_code": "Solidity code or a link to the verified source.",
            "use_case": "Intended application (e.g., 'auto-compounding LP rewards', 'swap optimiser')."
        }
        examples = [
            # Explain dynamic fee hook
            "Explain the dynamic fee hook and its use case.",
            # Analyse a pool
            "Analyse the ETH/USDC pool and its current hook combination.",
            # Breakdown of hook combination
            "Give a breakdown of the dynamic fee and TWAMM hook combination for the WETH/USDC pool. Include benefits and risks."
        ]
        return PromptDefinition(template=template, fields=fields, examples=examples)

    # Expose a registry of available prompt types for convenience
    registry: Dict[str, callable] = {
        "swap": swap.__func__,  # static method requires __func__ to get function object
        "liquidity_provision": liquidity_provision.__func__,
        "bridge": bridge.__func__,
        "hook_deployment": hook_deployment.__func__,
        "contract_analysis": contract_analysis.__func__,
    }


__all__ = ["MantuaPromptTemplates", "PromptDefinition"]
