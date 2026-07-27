"""Shared LLM helper for all agent nodes."""

import os

import structlog
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama

from src.config.settings import settings

logger = structlog.get_logger()


async def call_llm(system_prompt: str, user_prompt: str) -> AIMessage:
    """Call the configured LLM with system and user prompts."""
    ollama_host = os.environ.get("OLLAMA_HOST")
    api_key = os.environ.get("OLLAMA_API_KEY", "")

    logger.info(
        "llm_call",
        model=settings.llm_model,
        host=ollama_host or "localhost",
        has_key=bool(api_key),
    )

    llm = ChatOllama(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
        base_url=ollama_host,
        client_kwargs={"headers": {"Authorization": f"Bearer {api_key}"}}
        if api_key
        else {},
    )
    return await llm.ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
