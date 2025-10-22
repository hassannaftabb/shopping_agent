from __future__ import annotations

from livekit.plugins import deepgram
from ..config import get_settings


def create_deepgram_stt(
    model: str | None = None,
    language: str | None = None,
    api_key: str | None = None,
) -> "deepgram.STT":
    s = get_settings()
    return deepgram.STT(
        model=model or s.deepgram_model,
        api_key=(api_key or s.deepgram_api_key or ""),
        language=language or "en-US",
        smart_format=True,
        interim_results=True,
        no_delay=True,
        numerals=True,
    )


def create_stt_provider(api_key: str, model: str = "nova-3") -> "deepgram.STT":
    return create_deepgram_stt(model=model, api_key=api_key)