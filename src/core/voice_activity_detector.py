"""
voice_activity_detector.py - Lightweight energy-based VAD for Phase 2.
"""

import numpy as np


class VoiceActivityDetector:
    """Simple RMS-energy VAD with silence timeout."""

    def __init__(self, energy_threshold: float = 350.0, silence_seconds: float = 1.0, sample_rate: int = 16000, chunk_size: int = 1024):
        self.energy_threshold = energy_threshold
        self.silence_seconds = silence_seconds
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self._silence_chunks = 0

    def is_speech(self, frame: np.ndarray) -> bool:
        if frame is None or len(frame) == 0:
            return False
        rms = float(np.sqrt(np.mean(np.square(frame.astype(np.float32)))))
        return rms >= self.energy_threshold

    def update_and_should_stop(self, frame: np.ndarray) -> bool:
        """Returns True when silence lasted long enough to end an utterance."""
        if self.is_speech(frame):
            self._silence_chunks = 0
            return False

        self._silence_chunks += 1
        silent_for = (self._silence_chunks * self.chunk_size) / \
            float(self.sample_rate)
        return silent_for >= self.silence_seconds

    def reset(self) -> None:
        self._silence_chunks = 0
