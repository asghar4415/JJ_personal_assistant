"""
audio_pipeline.py - Phase 2 continuous listening orchestration.
"""

from __future__ import annotations

import logging
from typing import Callable, Optional

from src.pipeline.state_manager import StateManager, AssistantState

logger = logging.getLogger(__name__)


class AudioPipeline:
    """Continuous loop: wake-word listening -> query processing."""

    def __init__(self, audio_engine, wake_word_detector, vad, query_pipeline):
        self.audio_engine = audio_engine
        self.wake_word_detector = wake_word_detector
        self.vad = vad
        self.query_pipeline = query_pipeline
        self.state = StateManager()
        self._running = False

    def start_listening(self, on_event: Optional[Callable[[str], None]] = None, max_queries: Optional[int] = None):
        """
        Start continuous listening loop.

        Ctrl+C should be used by caller to stop loop in interactive scenarios.
        """
        if not self.wake_word_detector.enabled:
            self.state.set_state(AssistantState.ERROR,
                                 "Wake word backend unavailable")
            self._emit(
                on_event, "Wake word backend unavailable. Install/configure OpenWakeWord models for Phase 2 live mode.")
            return

        self._running = True
        processed = 0
        self.state.set_state(
            AssistantState.LISTENING_WAKE_WORD, "Listening for wake word")
        self._emit(on_event, "Listening for wake word...")

        try:
            for frame in self.audio_engine.stream_audio(duration=None):
                if not self._running:
                    break

                if self.wake_word_detector.detect(frame):
                    self._emit(
                        on_event, "Wake word detected. Capturing query...")
                    self.state.set_state(
                        AssistantState.CAPTURING_QUERY, "Wake word detected")

                    self.state.set_state(
                        AssistantState.PROCESSING_QUERY, "Running query pipeline")
                    result = self.query_pipeline.process_query(
                        audio_duration=5.0, enable_tts=True)

                    if result.get("success"):
                        self._emit(on_event, "Query handled successfully.")
                    else:
                        self._emit(
                            on_event, f"Query failed: {result.get('error', 'unknown error')}")

                    processed += 1
                    self.state.set_state(
                        AssistantState.LISTENING_WAKE_WORD, "Listening for next wake word")

                    if max_queries is not None and processed >= max_queries:
                        break

        except KeyboardInterrupt:
            logger.info("Audio pipeline interrupted")
        finally:
            self._running = False
            self.state.set_state(AssistantState.STOPPED,
                                 "Audio pipeline stopped")
            self._emit(on_event, "Continuous listening stopped.")

    def stop(self) -> None:
        self._running = False

    def get_info(self) -> dict:
        return {
            "running": self._running,
            "state": self.state.as_dict(),
            "wake_word": self.wake_word_detector.get_info(),
        }

    @staticmethod
    def _emit(callback: Optional[Callable[[str], None]], message: str) -> None:
        if callback:
            callback(message)
