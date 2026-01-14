from __future__ import annotations

import os
from dotenv import load_dotenv

from livekit import agents

from .core import ShopAgent
from .config import get_settings


def prepare_agent():
    """Prepare agent instance and environment."""
    load_dotenv()
    settings = get_settings()

    # Verify required settings
    if not settings.livekit_url:
        print("ERROR: LIVEKIT_URL not set in .env file")
        return None
    
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        print("ERROR: LIVEKIT_API_KEY and LIVEKIT_API_SECRET must be set in .env file")
        return None

    for key, value in [
        ("LIVEKIT_URL", settings.livekit_url),
        ("LIVEKIT_TOKEN", settings.livekit_token),
        ("LIVEKIT_API_KEY", settings.livekit_api_key),
        ("LIVEKIT_API_SECRET", settings.livekit_api_secret),
        ("DEEPGRAM_API_KEY", settings.deepgram_api_key),
        ("OPENAI_API_KEY", settings.openai_api_key),
        ("CARTESIA_API_KEY", settings.cartesia_api_key),
        ("CARTESIA_VOICE_ID", settings.cartesia_voice_id),
    ]:
        if value:
            os.environ[key] = value

    agent = ShopAgent()
    
    print("=" * 60)
    print("Starting Shop Whisper Agent...")
    print(f"LiveKit URL: {settings.livekit_url}")
    print(f"API Key: {settings.livekit_api_key[:10]}..." if settings.livekit_api_key else "API Key: NOT SET")
    print(f"API Secret: {'SET' if settings.livekit_api_secret else 'NOT SET'}")
    print("=" * 60)
    print("Agent configured for AUTO-DISPATCH")
    print("(Agent will automatically join rooms when participants connect)")
    print("=" * 60)
    print("Waiting for room connections...")
    print("(Check logs below when a participant joins a room)")
    print("=" * 60)
    
    return agent


def main():
    """Main entry point - called by CLI."""
    agent = prepare_agent()
    if agent is None:
        return
    
    # The CLI will call this with the appropriate command (dev/start)
    # Note: When agent_name is set, agents require explicit dispatch
    # Remove agent_name to allow auto-dispatch, or use explicit dispatch in token/API
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=agent.entrypoint,
            # agent_name="shop-whisper-agent",  # Commented out to allow auto-dispatch
            job_memory_warn_mb=1024,
        ),
    )


if __name__ == "__main__":
    main()
