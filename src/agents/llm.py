"""Shared LLM helper for all agent nodes."""

import structlog
from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama

from src.config.settings import settings

logger = structlog.get_logger()

_llm: ChatOllama | None = None


def _get_llm() -> ChatOllama:
    """Return a cached ChatOllama client (reused across agent calls)."""
    global _llm
    if _llm is None:
        api_key = settings.ollama_api_key
        _llm = ChatOllama(
            model=settings.llm_model,
            temperature=settings.llm_temperature,
            base_url=settings.ollama_host,
            client_kwargs={"headers": {"Authorization": f"Bearer {api_key}"}}
            if api_key
            else {},
        )
    return _llm


async def call_llm(system_prompt: str, user_prompt: str) -> AIMessage:
    """Call the configured LLM with system and user prompts."""
    logger.info(
        "llm_call",
        model=settings.llm_model,
        host=settings.ollama_host,
        has_key=bool(settings.ollama_api_key),
    )

    return await _get_llm().ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
