from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .types import CallResult, OrderResult


class DataKey(Enum):
    CUSTOMER_NAME = "customer_name"
    PRODUCT_SELECTION = "product_selection"
    EMAIL = "email"
    SCRIPT_STAGE = "script_stage"
    SUMMARY = "summary"


@dataclass
class CallSession:
    customer_name: Optional[str] = None
    product_selection: Optional[str] = None
    email: Optional[str] = None
    script_stage: str = "intro"
    summary: Optional[str] = None
    is_ai_completed: bool = False
    start_time: datetime = field(default_factory=lambda: datetime.now(tz=UTC))


class SessionManager:
    def __init__(self, results_file: str = "orders.csv"):
        self.results_file = results_file
        self.session = CallSession()
        self._ensure_csv_headers()

    def _ensure_csv_headers(self):
        if not os.path.exists(self.results_file):
            with open(self.results_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "customer_name", "product", "email", "order_id", "tracking_id", "summary"])

    def update_data(self, key: DataKey, value: str):
        """Update session data with key-value pair."""
        if not value or not value.strip():
            return

        value = value.strip()
        
        if key == DataKey.CUSTOMER_NAME:
            self.session.customer_name = value
            print(f"Customer name updated: {value}")
            
        elif key == DataKey.PRODUCT_SELECTION:
            self.session.product_selection = value
            print(f"Product selection updated: {value}")
                
        elif key == DataKey.EMAIL:
            self.session.email = value
            print(f"Email updated: {value}")
            
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
            basic_summary = f"Order completed by AI"
            if self.session.product_selection:
                basic_summary += f" - Product: {self.session.product_selection}"
            return basic_summary
        else:
            return "Call hung up by user"

    def save_order_data(self, order_id: str, tracking_id: str):
        """Save order data to CSV."""
        if not self.session.customer_name or not self.session.product_selection:
            print("No order data to save")
            return None

        result = OrderResult(
            timestamp=self.session.start_time.isoformat(),
            customer_name=self.session.customer_name or "Unknown",
            product=self.session.product_selection or "Unknown",
            email=self.session.email or "Unknown",
            order_id=order_id,
            tracking_id=tracking_id,
            summary=self.generate_summary()
        )

        with open(self.results_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                result.timestamp,
                result.customer_name,
                result.product,
                result.email,
                result.order_id,
                result.tracking_id,
                result.summary
            ])

        print(f"Order data saved:")
        print(f"   Customer: {result.customer_name}")
        print(f"   Product: {result.product}")
        print(f"   Email: {result.email}")
        print(f"   Order ID: {result.order_id}")
        print(f"   Tracking ID: {result.tracking_id}")
        print(f"   Summary: {result.summary}")

        return result
