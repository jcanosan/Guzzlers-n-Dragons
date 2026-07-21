"""Shared LLM helper for all agent nodes."""

from langchain_core.messages import AIMessage
from langchain_ollama import ChatOllama

from src.config.settings import settings


async def call_llm(system_prompt: str, user_prompt: str) -> AIMessage:
    """Call the configured LLM with system and user prompts."""
    llm = ChatOllama(
        model=settings.llm_model,
        temperature=settings.llm_temperature,
    )
    return await llm.ainvoke(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
