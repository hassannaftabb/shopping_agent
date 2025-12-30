from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol


class STTProvider(Protocol):
    async def transcribe(self, audio: bytes, sample_rate: int) -> str: ...


class LLMProvider(Protocol):
    async def generate(self, prompt: str, history: Optional[List[Dict[str, Any]]] = None) -> str: ...


class TTSProvider(Protocol):
    async def synthesize(self, text: str, sample_rate: int) -> bytes: ...


@dataclass(slots=True)
class CallResult:
    timestamp: str
    candidate_name: str
    interest_status: str
    summary: str


@dataclass(slots=True)
class OrderResult:
    timestamp: str
    customer_name: str
    product: str
    email: str
    order_id: str
    tracking_id: str
    summary: str


@dataclass(slots=True)
class AgentPipeline:
    stt: STTProvider
    llm: LLMProvider
    tts: TTSProvider
    sample_rate: int = 16000

    async def process_audio(
        self, 
        audio: bytes, 
        history: Optional[List[Dict[str, Any]]] = None
    ) -> tuple[str, bytes]:
        text = await self.stt.transcribe(audio, self.sample_rate)
        reply = await self.llm.generate(text, history=history)
        speech = await self.tts.synthesize(reply, self.sample_rate)
        return reply, speech
