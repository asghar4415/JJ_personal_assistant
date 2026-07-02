"""
wake_word_detector.py - Wake word detector using OpenWakeWord.
"""

import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class WakeWordDetector:
    """Detects wake word using OpenWakeWord pre-trained/custom models."""

    def __init__(self, keyword: str = "Hey JJ", model_name: str = "hey_mycroft", threshold: float = 0.5):
        self.keyword = keyword
        self.model_name = model_name
        self.threshold = threshold
        self.enabled = False
        self.backend = "none"
        self._model = None
        self.frame_length = 1280
        self._buffer = np.array([], dtype=np.int16)
        self._try_init_openwakeword()

    def _try_init_openwakeword(self) -> None:
        try:
            import openwakeword
            from openwakeword.model import Model
            from openwakeword.utils import download_models

            models_dir = Path(openwakeword.__file__).resolve(
            ).parent / "resources" / "models"
            model_basename = self.model_name.replace(" ", "_")
            onnx_target = models_dir / f"{model_basename}_v0.1.onnx"

            if not onnx_target.exists():
                logger.info(
                    f"Downloading OpenWakeWord models for '{self.model_name}'...")
                download_models(
                    model_names=[model_basename], target_directory=str(models_dir))

            self._model = Model(
                wakeword_models=[self.model_name],
                inference_framework="onnx",
            )
            self.backend = "openwakeword"
            self.enabled = True
        except Exception as exc:
            logger.warning(f"OpenWakeWord init failed: {exc}")
            self._model = None
            self.backend = "none"
            self.enabled = False

    def detect(self, frame: np.ndarray) -> bool:
        if not self.enabled or self._model is None:
            return False

        if frame is None or len(frame) == 0:
            return False

        pcm = frame.astype(np.int16)
        self._buffer = np.concatenate([self._buffer, pcm])

        detected = False
        while len(self._buffer) >= self.frame_length:
            chunk = self._buffer[: self.frame_length]
            self._buffer = self._buffer[self.frame_length:]

            prediction = self._model.predict(chunk)
            score = float(prediction.get(self.model_name, 0.0))
            if score >= self.threshold:
                detected = True
                break

        return detected

    def close(self) -> None:
        self._model = None
        self._buffer = np.array([], dtype=np.int16)

    def get_info(self) -> dict:
        return {
            "enabled": self.enabled,
            "backend": self.backend,
            "keyword": self.keyword,
            "model_name": self.model_name,
            "threshold": self.threshold,
        }
