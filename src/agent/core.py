from __future__ import annotations

import asyncio
import csv
import logging
import os
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from agent.constants import get_script_variables
from livekit import agents, api, rtc
from livekit.agents import AgentSession, RoomInputOptions, RoomOutputOptions
from livekit.agents.voice import Agent
from livekit.plugins import noise_cancellation, silero
from livekit.plugins.turn_detector.english import EnglishModel

from .config import get_recruiter_prompt, get_settings
from .providers import create_llm_provider, create_stt_provider, create_tts_provider
from .session import SessionManager
from .tools import create_data_collection_tool
from .types import CallResult

logger = logging.getLogger("recruiter_agent")
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


class RecruiterAgent:
    def __init__(self):
        self.settings = get_settings()
        self.results_file = "call_results.csv"
        self.session_manager = SessionManager(self.results_file)
        self._call_completed = False
        self._ensure_csv_headers()

    def _ensure_csv_headers(self):
        if not os.path.exists(self.results_file):
            with open(self.results_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "candidate_name", "interest_status", "summary"])

    def _save_result(self, result: CallResult):
        with open(self.results_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([result.timestamp, result.candidate_name, result.interest_status, result.summary])

    async def _hangup_call(self, ctx: agents.JobContext):
        try:
            if not self._call_completed:
                logger.info("Saving session data before hangup")
                self.session_manager.save_session_data()
                self._call_completed = True
            
            logger.info("Hanging up call")
            await ctx.api.room.delete_room(api.DeleteRoomRequest(room=ctx.room.name))
            logger.info(f"Deleted room {ctx.room.name}")
        except Exception as e:
            logger.warning(f"Could not delete room: {e}")

    async def _on_disconnected(self, ctx: agents.JobContext):
        logger.info("Room disconnected - performing cleanup")
        # Don't call hangup again if already completed
        if not self._call_completed:
            await self._hangup_call(ctx)

    async def _force_hangup_if_empty(self, ctx: agents.JobContext):
        await asyncio.sleep(3)
        try:
            req = api.ListParticipantsRequest(room=ctx.room.name)
            async with ctx.api:
                resp = await ctx.api.room.list_participants(req)
                participants = resp.participants
            if len(participants) <= 1:
                logger.info("No human participants remain - closing room")
                await self._hangup_call(ctx)
        except Exception as e:
            logger.warning(f"Force cleanup check failed: {e}")

    async def _watchdog(self, ctx: agents.JobContext):
        await asyncio.sleep(60)
        logger.warning("Watchdog timeout - forcing hangup")
        await self._hangup_call(ctx)

    async def entrypoint(self, ctx: agents.JobContext):
        start_time = datetime.now(tz=UTC)
        logger.info(f"Agent started at {start_time.isoformat()}")

        try:
            await ctx.connect()
            logger.info(f"Connected to room: {ctx.room.name}")

            participant = await ctx.wait_for_participant()
            logger.info(f"Participant connected: {participant.identity}")

            stt = create_stt_provider(self.settings.deepgram_api_key, self.settings.deepgram_model)
            llm = create_llm_provider(self.settings.openai_api_key, self.settings.openai_model)
            tts = create_tts_provider(
                self.settings.cartesia_api_key,
                self.settings.cartesia_voice_id,
                self.settings.cartesia_model,
                self.settings.cartesia_format
            )

            data_collection_tool = create_data_collection_tool(self.session_manager)

            voice_agent = Agent(
                instructions=get_recruiter_prompt(),
                stt=stt,
                llm=llm,
                tts=tts,
                tools=[data_collection_tool],
                vad=silero.VAD.load(),
                turn_detection=EnglishModel(),
            )

            call_session = AgentSession(stt=stt, llm=llm, tts=tts)

            await call_session.start(
                room=ctx.room,
                agent=voice_agent,
                room_output_options=RoomOutputOptions(transcription_enabled=True),
                room_input_options=RoomInputOptions(noise_cancellation=noise_cancellation.BVCTelephony()),
            )

            logger.info("Agent session started. Awaiting room disconnection...")
            await call_session.generate_reply(
                instructions=f"Say exactly this phrase and nothing else: '{get_script_variables().intro_greeting}'.",
                allow_interruptions=False,
            )        
            # Monitor for call completion
            call_completed = False
            
            @call_session.on(event="function_tools_executed")
            def on_function_tools_executed(event) -> None:
                """Handle function tools executed event."""
                nonlocal call_completed
                for function_call, output in event.zipped():
                    print(f"Function call: {function_call.name}, Output: {output.output}")
                    if function_call.name == "collect_data" and not output.output:
                        logger.info("Summary provided - call completed by AI")
                        call_completed = True
                        self._call_completed = True
                        self.session_manager.save_session_data()
                        asyncio.create_task(self._delayed_hangup(ctx))
                        break

            ctx.add_shutdown_callback(lambda: self._on_disconnected(ctx))

            @ctx.room.on("participant_disconnected")
            def participant_disconnected(p: rtc.Participant):
                logger.info(f"Participant disconnected: {p.identity}")
                asyncio.create_task(self._force_hangup_if_empty(ctx))

            asyncio.create_task(self._watchdog(ctx))

            await asyncio.Event().wait()

        except Exception as e:
            logger.error(f"Fatal error in entrypoint: {e}", exc_info=True)
            await self._hangup_call(ctx)
        finally:
            logger.info("Agent shutting down")

    async def _delayed_hangup(self, ctx: agents.JobContext):
        """Hang up after a brief delay to allow final response."""
        await asyncio.sleep(2)
        logger.info("Call completion detected - hanging up call")
        await self._hangup_call(ctx)
