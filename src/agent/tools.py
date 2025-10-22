from __future__ import annotations

from typing import Any, Dict

from livekit.agents import RunContext, function_tool

from .session import DataKey, SessionManager


def build_data_collection_schema() -> Dict[str, Any]:
    """Build schema for data collection tool."""
    return {
        "name": "collect_data",
        "description": "Call this tool whenever you extract key information from the conversation. When the call is complete and you've said goodbye, call this with summary to finalize the call.",
        "parameters": {
            "type": "object",
            "properties": {
                "interest_status": {
                    "type": "string",
                    "description": "Current interest status: 'Interested', 'Not Interested', or 'Asked for more details'",
                    "enum": ["Interested", "Not Interested", "Asked for more details"],
                    "default": ""
                },
                "decline_reason": {
                    "type": "string",
                    "description": "If not interested, the specific reason given (salary, location, timing, etc.)",
                    "default": ""
                },
                "script_stage": {
                    "type": "string",
                    "description": "Current stage of the script",
                    "enum": ["intro", "reason", "decline_handling", "engagement", "closing"],
                    "default": ""
                },
                "summary": {
                    "type": "string",
                    "description": "Final summary of the call (only provide when call is complete and you've said goodbye)",
                    "default": ""
                }
            },
            "required": [],
            "additionalProperties": False,
        },
    }


def create_data_collection_tool(session_manager: SessionManager) -> Any:
    """Create data collection tool for tracking conversation data."""
    schema = build_data_collection_schema()

    @function_tool(raw_schema=schema)
    async def collect_data_handler(raw_arguments: Dict[str, Any], context: RunContext) -> str:
        """Handle data collection during conversation."""
        try:
            interest_status = str(raw_arguments.get("interest_status", "")).strip()
            decline_reason = str(raw_arguments.get("decline_reason", "")).strip()
            script_stage = str(raw_arguments.get("script_stage", "")).strip()
            summary = str(raw_arguments.get("summary", "")).strip()

            # Update data using the unified method
            if interest_status:
                session_manager.update_data(DataKey.INTEREST_STATUS, interest_status)
            
            if decline_reason:
                session_manager.update_data(DataKey.DECLINE_REASON, decline_reason)
            
            if script_stage:
                session_manager.update_data(DataKey.SCRIPT_STAGE, script_stage)
            
            if summary:
                session_manager.update_data(DataKey.SUMMARY, summary)
                return None

            return "Data collected successfully"

        except Exception as e:
            print(f"❌ Error collecting data: {e}")
            return f"Error collecting data: {str(e)}"

    return collect_data_handler