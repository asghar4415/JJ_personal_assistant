"""
state_manager.py - Runtime state management for JJ audio pipeline.
"""

from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class AssistantState(str, Enum):
    IDLE = "idle"
    LISTENING_WAKE_WORD = "listening_wake_word"
    CAPTURING_QUERY = "capturing_query"
    PROCESSING_QUERY = "processing_query"
    SPEAKING_RESPONSE = "speaking_response"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class StateSnapshot:
    state: AssistantState
    updated_at: str = field(
        default_factory=lambda: datetime.utcnow().isoformat())
    message: str = ""


class StateManager:
    """Tracks assistant runtime state transitions."""

    def __init__(self):
        self._snapshot = StateSnapshot(
            state=AssistantState.IDLE, message="Initialized")

    def set_state(self, state: AssistantState, message: str = "") -> None:
        self._snapshot = StateSnapshot(state=state, message=message)

    def get_state(self) -> StateSnapshot:
        return self._snapshot

    def as_dict(self) -> dict:
        return {
            "state": self._snapshot.state.value,
            "updated_at": self._snapshot.updated_at,
            "message": self._snapshot.message,
        }
