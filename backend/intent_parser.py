"""Natural language intent parser.

The intent parser translates free‑form user input into structured commands
understood by the backend.  This module implements both a simple rule‑based
parser and an optional integration with a fine‑tuned language model.  The
rule‑based parser acts as a fast fallback when the model is disabled or
unavailable.
"""

import re
from typing import Dict, Optional

import httpx

from .config import settings
from .errors import IntentParsingError
from .models import ActionType, Intent


def _call_openai_intent_parser(prompt: str) -> Optional[Intent]:
    """Call the fine‑tuned OpenAI model to parse the intent.

    This function sends a request to the OpenAI API using the configured
    fine‑tuned model.  It returns an `Intent` object if the call succeeds
    or ``None`` if the model could not be reached.

    Note: network errors are swallowed and reported via the return value.
    """

    api_key = settings.openai_api_key
    model_name = settings.fine_tuned_model
    if not api_key:
        return None
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    # The prompt instructs the model to return a JSON with action, parameters and confidence
    messages = [
        {
            "role": "system",
            "content": (
                "You are an intent parser for a DEX assistant. Given a user query, "
                "return a JSON object with fields 'action', 'parameters' and 'confidence'. "
                "Action must be one of 'query', 'swap', 'add_liquidity', 'execute', 'custom'."
            ),
        },
        {"role": "user", "content": prompt},
    ]
    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": 256,
        "temperature": 0.0,
    }
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"].strip()
        # Expect the model to return a JSON dictionary
        parsed = httpx.Response(200, text=content).json()
        return Intent(
            action=ActionType(parsed["action"]),
            parameters=parsed.get("parameters", {}),
            confidence=float(parsed.get("confidence", 0.0)),
        )
    except Exception:
        return None


def _rule_based_parser(prompt: str) -> Intent:
    """Very simple rule‑based parser as a fallback.

    This implementation looks for keywords and number patterns to infer the action
    and parameters.  It is intentionally conservative; unknown patterns fall
    back to a general query.
    """

    text = prompt.lower()

    # Determine action
    if any(keyword in text for keyword in ["swap", "trade", "exchange"]):
        action = ActionType.SWAP
    elif any(keyword in text for keyword in ["add liquidity", "provide liquidity", "lp"]):
        action = ActionType.ADD_LIQUIDITY
    elif any(keyword in text for keyword in ["execute", "send transaction"]):
        action = ActionType.EXECUTE
    else:
        action = ActionType.QUERY

    parameters: Dict[str, str] = {}

    # Extract token symbols (heuristically assume uppercase letters)
    tokens = re.findall(r"\b[A-Z]{2,5}\b", prompt)
    if action == ActionType.SWAP and len(tokens) >= 2:
        # Assume first token is input, second is output
        parameters["token_in"] = tokens[0]
        parameters["token_out"] = tokens[1]
    elif action == ActionType.ADD_LIQUIDITY and len(tokens) >= 2:
        parameters["token_a"] = tokens[0]
        parameters["token_b"] = tokens[1]

    # Extract numeric amount(s)
    numbers = re.findall(r"(\d*\.?\d+)", prompt)
    if numbers:
        # Use the first number as amount; additional numbers could specify slippage or other fields
        parameters["amount"] = numbers[0]
        if len(numbers) > 1:
            parameters.setdefault("amount_b", numbers[1])

    # Extract hook address (0x...) if present
    match = re.search(r"0x[a-fA-F0-9]{40}", prompt)
    if match:
        parameters["hook_address"] = match.group(0)

    return Intent(action=action, parameters=parameters, confidence=0.5)


def parse_intent(prompt: str) -> Intent:
    """Public entrypoint for parsing intents.

    If enabled and configured, a fine‑tuned OpenAI model is used first.  If the
    model call fails or is disabled, the rule‑based parser is used as a
    fallback.  An `IntentParsingError` is raised only in the unlikely event
    that both methods fail.
    """

    if settings.enable_intent_parser and settings.openai_api_key:
        intent = _call_openai_intent_parser(prompt)
        if intent is not None:
            return intent

    # Fallback to rule‑based parser
    intent = _rule_based_parser(prompt)
    if intent is None:
        raise IntentParsingError("Unable to parse intent")
    return intent