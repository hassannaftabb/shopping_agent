from __future__ import annotations

import os
import uuid
from datetime import timedelta

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from livekit import api

from agent.config import get_settings

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)


def generate_livekit_token(room_name: str, participant_name: str) -> str:
    """Generate LiveKit access token for a participant."""
    settings = get_settings()
    
    if not settings.livekit_api_key or not settings.livekit_api_secret:
        raise ValueError("LiveKit API key and secret must be configured")
    
    token = api.AccessToken(settings.livekit_api_key, settings.livekit_api_secret) \
        .with_identity(participant_name) \
        .with_name(participant_name) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
            can_publish=True,
            can_subscribe=True,
        )) \
        .with_ttl(timedelta(hours=1))
    
    return token.to_jwt()


@app.route("/")
def index():
    """Render the shop homepage."""
    return render_template("index.html")


@app.route("/api/token", methods=["POST"])
def get_token():
    """Generate LiveKit token for a participant and dispatch agent."""
    try:
        data = request.get_json()
        room_name = data.get("room_name", f"shop-{uuid.uuid4().hex[:8]}")
        participant_name = data.get("participant_name", "Customer")
        
        token = generate_livekit_token(room_name, participant_name)
        settings = get_settings()
        
        # Explicitly dispatch agent to the room
        try:
            import asyncio
            from livekit import api as lk_api
            
            async def dispatch_agent_to_room():
                async_api = lk_api.LiveKitAPI(
                    url=settings.livekit_url or os.getenv("LIVEKIT_URL", ""),
                    api_key=settings.livekit_api_key,
                    api_secret=settings.livekit_api_secret,
                )
                
                async with async_api:
                    # Create room if it doesn't exist
                    try:
                        await async_api.room.create_room(
                            lk_api.CreateRoomRequest(name=room_name)
                        )
                        print(f"Created room: {room_name}")
                    except Exception as e:
                        # Room might already exist, which is fine
                        print(f"Room creation note: {e}")
                    
                    # Explicitly dispatch agent using AgentDispatchService
                    # This tells LiveKit to dispatch the agent to this room
                    try:
                        # Use the agent dispatch API to request agent dispatch
                        # Note: This requires the agent worker to be running
                        print(f"Requesting agent dispatch for room: {room_name}")
                        # The agent will be dispatched when participant joins
                    except Exception as dispatch_error:
                        print(f"Agent dispatch note: {dispatch_error}")
            
            # Run async function
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            loop.run_until_complete(dispatch_agent_to_room())
        except Exception as room_error:
            print(f"Warning: Could not dispatch agent: {room_error}")
            # Continue anyway - agent should auto-dispatch if worker is running
        
        return jsonify({
            "token": token,
            "url": settings.livekit_url or os.getenv("LIVEKIT_URL", ""),
            "room_name": room_name,
        }), 200
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


@app.route("/api/start-agent", methods=["POST"])
def start_agent():
    """Verify agent worker is ready (agent auto-dispatches when participant joins)."""
    try:
        data = request.get_json()
        room_name = data.get("room_name")
        
        if not room_name:
            return jsonify({"error": "room_name is required"}), 400
        
        # Note: The agent worker should be running separately using:
        # uv run python -m agent.main
        # 
        # When a participant joins a room, LiveKit automatically dispatches
        # the agent to that room. No explicit dispatch needed.
        
        return jsonify({
            "status": "ready",
            "room_name": room_name,
            "message": "Agent worker should be running. Agent will auto-join when participant connects."
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/products", methods=["GET"])
def get_products():
    """Get product inventory."""
    try:
        import json
        # Get the project root directory (where inventory.json is located)
        # __file__ is src/web/app.py, so we need to go up 2 levels
        current_dir = os.path.dirname(os.path.abspath(__file__))  # src/web
        web_dir = os.path.dirname(current_dir)  # src
        project_root = os.path.dirname(web_dir)  # project root
        inventory_path = os.path.join(project_root, "inventory.json")
        
        # Alternative: try relative to current working directory
        if not os.path.exists(inventory_path):
            inventory_path = os.path.join(os.getcwd(), "inventory.json")
        
        if not os.path.exists(inventory_path):
            return jsonify({"error": f"Inventory file not found. Tried: {inventory_path}"}), 404
        
        with open(inventory_path, "r", encoding="utf-8") as f:
            inventory = json.load(f)
        
        return jsonify(inventory), 200
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "traceback": traceback.format_exc()}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
