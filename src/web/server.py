from __future__ import annotations

from dotenv import load_dotenv

from .app import app
from agent.config import get_settings


def main():
    """Main entry point for the web server."""
    load_dotenv()
    settings = get_settings()
    
    print("=" * 60)
    print("Zenitheon Shop - Web Server")
    print("=" * 60)
    print(f"Starting web server on http://localhost:5000")
    print(f"LiveKit URL: {settings.livekit_url}")
    print("=" * 60)
    
    app.run(debug=True, host="0.0.0.0", port=5000)


if __name__ == "__main__":
    main()
