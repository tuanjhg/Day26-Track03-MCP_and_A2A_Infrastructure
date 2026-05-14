"""Shared LLM factory for all agents.

Uses OpenRouter as an OpenAI-compatible API, so any provider's model
can be selected via the OPENROUTER_MODEL env var.
"""

import os

from langchain_openai import ChatOpenAI


def get_llm():
    """Return a ChatOpenAI client pointed at OpenRouter."""
    if os.getenv("LAB_OFFLINE_MODE") == "1":
        from common.offline_llm import OfflineLLM

        return OfflineLLM()

    return ChatOpenAI(
        model=os.getenv("OPENROUTER_MODEL", "openrouter/free"),
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        openai_api_base="https://openrouter.ai/api/v1",
        temperature=0.3,
    )
