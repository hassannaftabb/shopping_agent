from __future__ import annotations

from livekit.plugins import openai as lk_openai
from ..config import get_settings


def create_openai_llm(
    model: str | None = None,
    api_key: str | None = None,
) -> "lk_openai.LLM":
    s = get_settings()
    return lk_openai.LLM(
        model=(model or s.openai_model),
        api_key=(api_key or s.openai_api_key or ""),
        temperature=0.3,
    )


def create_llm_provider(api_key: str, model: str = "gpt-4o-mini") -> "lk_openai.LLM":
    return create_openai_llm(model=model, api_key=api_key)