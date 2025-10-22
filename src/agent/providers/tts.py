from __future__ import annotations

from livekit.plugins import cartesia
from ..config import get_settings


def create_cartesia_tts(
    voice_id: str | None = None,
    model: str | None = None,
    api_key: str | None = None,
    sample_rate: int | None = None,
) -> "cartesia.TTS":
    s = get_settings()
    return cartesia.TTS(
        api_key=(api_key or s.cartesia_api_key or ""),
        voice=(voice_id or s.cartesia_voice_id or ""),
        model=(model or s.cartesia_model),
        sample_rate=(sample_rate or s.sample_rate_hz),
    )


def create_tts_provider(
    api_key: str, 
    voice_id: str, 
    model: str = "sonic-2",
    format: str = "wav"
) -> "cartesia.TTS":
    return create_cartesia_tts(voice_id=voice_id, model=model, api_key=api_key)