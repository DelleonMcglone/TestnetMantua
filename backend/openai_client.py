"""Wrapper around the OpenAI API with fallback support.

This helper module centralises calls to OpenAI's completions API.  It
automatically supplies the API key from environment via settings and
supports specifying a preferred model with a fallback to GPT‑4.  All
timeouts and errors are handled uniformly and surfaced as exceptions.
"""

import logging
from typing import List, Optional

import openai

from .config import settings

log = logging.getLogger(__name__)


def call_chat_completion(
    messages: List[dict],
    model: Optional[str] = None,
    temperature: float = 0.0,
    max_tokens: int = 256,
) -> str:
    """Call the OpenAI chat completion endpoint.

    Parameters
    ----------
    messages: list of dict
        Conversation history formatted for OpenAI (e.g.
        [{"role": "user", "content": "Hello"}]).
    model: str, optional
        The model to call.  If unspecified, defaults to settings.fine_tuned_model
        with a fallback to "gpt-4".
    temperature: float
        Sampling temperature.
    max_tokens: int
        Maximum number of tokens to generate.

    Returns
    -------
    str
        The assistant's reply.

    Raises
    ------
    RuntimeError
        If the API call fails after trying the fallback model.
    """
    api_key = settings.openai_api_key
    if not api_key:
        raise RuntimeError("OpenAI API key is not configured")
    openai.api_key = api_key
    chosen_model = model or settings.fine_tuned_model
    models_to_try = [chosen_model, "gpt-4"]
    last_exception = None
    for m in models_to_try:
        try:
            response = openai.ChatCompletion.create(
                model=m,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            content = response.choices[0].message["content"]
            return content
        except Exception as exc:  # broad catch: handle connection/timeouts and other errors
            log.warning("OpenAI call with model %s failed: %s", m, exc)
            last_exception = exc
            continue
    raise RuntimeError(f"All OpenAI model attempts failed: {last_exception}")


__all__ = ["call_chat_completion"]