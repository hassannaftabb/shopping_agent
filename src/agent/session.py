from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .types import CallResult


class DataKey(Enum):
    CANDIDATE_NAME = "candidate_name"
    INTEREST_STATUS = "interest_status"
    DECLINE_REASON = "decline_reason"
    SCRIPT_STAGE = "script_stage"
    SUMMARY = "summary"


@dataclass
class CallSession:
    candidate_name: Optional[str] = None
    interest_status: Optional[str] = None
    decline_reason: Optional[str] = None
    script_stage: str = "intro"
    summary: Optional[str] = None
    is_ai_completed: bool = False
    start_time: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


class SessionManager:
    def __init__(self, results_file: str = "call_results.csv"):
        self.results_file = results_file
        self.session = CallSession()
        self._ensure_csv_headers()

    def _ensure_csv_headers(self):
        if not os.path.exists(self.results_file):
            with open(self.results_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "candidate_name", "interest_status", "summary"])

    def update_data(self, key: DataKey, value: str):
        """Update session data with key-value pair."""
        if not value or not value.strip():
            return

        value = value.strip()
        
        if key == DataKey.CANDIDATE_NAME:
            self.session.candidate_name = value
            print(f"📝 Candidate name updated: {value}")
            
        elif key == DataKey.INTEREST_STATUS:
            if value in ["Interested", "Not Interested", "Asked for more details"]:
                self.session.interest_status = value
                print(f"📝 Interest status updated: {value}")
                
        elif key == DataKey.DECLINE_REASON:
            self.session.decline_reason = value
            print(f"📝 Decline reason updated: {value}")
            
            
        elif key == DataKey.SCRIPT_STAGE:
            self.session.script_stage = value
            print(f"📝 Script stage updated: {value}")
            
        elif key == DataKey.SUMMARY:
            self.session.summary = value
            self.session.is_ai_completed = True
            print(f"📝 Summary provided - call marked as AI completed: {value}")

    def is_summary_provided(self) -> bool:
        """Check if summary was provided (indicates call completion)."""
        return self.session.summary is not None and self.session.summary.strip() != ""

    def generate_summary(self) -> str:
        """Generate summary based on available data."""
        if self.session.is_ai_completed and self.session.summary:
            return self.session.summary
        elif self.session.is_ai_completed:
            # AI completed but no summary - create basic summary
            basic_summary = f"Call completed by AI"
            if self.session.decline_reason:
                basic_summary += f" - Reason: {self.session.decline_reason}"
            return basic_summary
        else:
            return "Call hung up by user"

    def save_session_data(self):
        """Save session data to CSV."""
        if not self.session.interest_status:
            print("📝 No significant data to save")
            return None

        from .constants import get_script_variables
        script_vars = get_script_variables()
        candidate_name = script_vars.candidate_name

        result = CallResult(
            timestamp=self.session.start_time.isoformat(),
            candidate_name=candidate_name,
            interest_status=self.session.interest_status or "Unknown",
            summary=self.generate_summary()
        )

        with open(self.results_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([result.timestamp, result.candidate_name, result.interest_status, result.summary])

        print(f"📊 Session data saved:")
        print(f"   Candidate: {result.candidate_name}")
        print(f"   Status: {result.interest_status}")
        print(f"   Summary: {result.summary}")

        return result
