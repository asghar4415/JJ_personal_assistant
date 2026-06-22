"""
speech_recognizer.py - Speech-to-Text using OpenAI Whisper

Provides transcription of audio to text with confidence scores and segment information.
"""

import numpy as np
import logging
from typing import Dict, List, Optional
import whisper

logger = logging.getLogger(__name__)


class SpeechRecognizer:
    """Speech-to-text transcription engine using Whisper"""

    def __init__(self, model_name: str = "tiny.en", device: str = "cpu", language: str = "en"):
        """
        Initialize Whisper speech recognizer

        Args:
            model_name: Whisper model size ("tiny.en", "base", "small", "medium", "large")
            device: Device to run on ("cpu" or "cuda")
            language: Language code (e.g., "en" for English)
        """
        self.model_name = model_name
        self.device = device
        self.language = language

        logger.info(f"Loading Whisper model: {model_name} on {device}")
        self.model = whisper.load_model(model_name, device=device)
        logger.info(f"Whisper model loaded successfully")

    def transcribe(self, audio_data: np.ndarray, sample_rate: int = 16000) -> Dict:
        """
        Transcribe audio to text

        Args:
            audio_data: numpy array of audio samples (int16 or float32)
            sample_rate: Sample rate in Hz (default: 16000)

        Returns:
            Dictionary with keys:
            - "text": Full transcribed text
            - "confidence": Confidence score (0-1)
            - "segments": List of segment dicts with time and text
            - "language": Detected/specified language
            - "duration": Audio duration in seconds
        """
        try:
            # Validate input
            if not isinstance(audio_data, np.ndarray):
                raise ValueError("audio_data must be numpy array")

            if len(audio_data) == 0:
                logger.warning("Empty audio data")
                return {
                    "text": "",
                    "confidence": 0.0,
                    "segments": [],
                    "language": self.language,
                    "duration": 0.0,
                }

            # Convert to float32 if needed (Whisper expects float32)
            if audio_data.dtype == np.int16:
                audio_float = audio_data.astype(np.float32) / 32768.0
            elif audio_data.dtype in [np.float32, np.float64]:
                audio_float = audio_data.astype(np.float32)
            else:
                audio_float = audio_data.astype(np.float32)

            # Calculate duration
            duration = len(audio_float) / sample_rate
            logger.info(f"Transcribing {duration:.2f}s of audio")

            # Transcribe
            result = self.model.transcribe(
                audio_float,
                language=self.language,
                fp16=False,  # Use float32 for stability
                verbose=False
            )

            # Extract segments
            segments = []
            if "segments" in result:
                for seg in result["segments"]:
                    segments.append({
                        "start": seg.get("start", 0),
                        "end": seg.get("end", 0),
                        "text": seg.get("text", "").strip(),
                    })

            # Calculate average confidence (Whisper doesn't provide per-segment confidence)
            # We estimate confidence based on no_speech_prob if available
            confidence = 1.0
            if segments and "no_speech_prob" in result:
                confidence = max(0.0, 1.0 - result["no_speech_prob"])

            transcription = {
                "text": result.get("text", "").strip(),
                "confidence": confidence,
                "segments": segments,
                "language": result.get("language", self.language),
                "duration": duration,
            }

            logger.info(
                f"Transcription complete: '{transcription['text'][:50]}...' (conf: {confidence:.2f})")
            return transcription

        except Exception as e:
            logger.error(f"Error in transcribe: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "segments": [],
                "language": self.language,
                "duration": 0.0,
            }

    def transcribe_file(self, filepath: str) -> Dict:
        """
        Transcribe audio from file

        Args:
            filepath: Path to audio file (WAV, MP3, etc.)

        Returns:
            Transcription result dictionary (see transcribe() for format)
        """
        try:
            logger.info(f"Loading audio file: {filepath}")
            audio = whisper.load_audio(filepath)
            return self.transcribe(audio)
        except Exception as e:
            logger.error(f"Error transcribing file {filepath}: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "segments": [],
                "language": self.language,
                "duration": 0.0,
            }

    def get_info(self) -> Dict:
        """Get recognizer configuration info"""
        return {
            "model": self.model_name,
            "device": self.device,
            "language": self.language,
        }
