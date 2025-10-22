from __future__ import annotations

import os
from dotenv import load_dotenv

from livekit import agents

from .core import RecruiterAgent
from .config import get_settings


def main():
    load_dotenv()
    settings = get_settings()

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

    agent = RecruiterAgent()
    
    print("Starting Recruiter Agent...")
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=agent.entrypoint,
            agent_name="recruiter-agent",
            job_memory_warn_mb=1024,
        ),
    )


if __name__ == "__main__":
    main()
