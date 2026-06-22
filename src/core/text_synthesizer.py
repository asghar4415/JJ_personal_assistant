"""
text_synthesizer.py - Text-to-Speech using pyttsx3

Provides text-to-speech synthesis with customizable voice, rate, and volume.
"""

import pyttsx3
import numpy as np
import logging
from typing import Dict, Optional
import io
import wave

logger = logging.getLogger(__name__)


class TextSynthesizer:
    """Text-to-speech synthesis engine using pyttsx3"""

    def __init__(self, rate: int = 150, volume: float = 1.0):
        """
        Initialize text synthesizer

        Args:
            rate: Speech rate in words per minute (default: 150)
            volume: Volume level 0.0-1.0 (default: 1.0)
        """
        self.rate = rate
        self.volume = volume

        logger.info(
            f"Initializing TextSynthesizer: rate={rate}wpm, volume={volume}")

        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)

            # Get available voices
            self.voices = self.engine.getProperty('voices')
            logger.info(f"Available voices: {len(self.voices)}")

            # Set default voice (first available)
            if self.voices:
                self.engine.setProperty('voice', self.voices[0].id)
                logger.info(f"Default voice: {self.voices[0].name}")

        except Exception as e:
            logger.error(f"Error initializing pyttsx3: {e}")
            raise

    def synthesize(self, text: str) -> np.ndarray:
        """
        Synthesize text to speech (in-memory)

        Note: pyttsx3 doesn't support direct in-memory audio export on all platforms.
        This method saves to a temporary WAV and reads it back.

        Args:
            text: Text to synthesize

        Returns:
            numpy array of audio samples (int16, 16kHz assumed)
        """
        if not text or not text.strip():
            logger.warning("Empty text provided to synthesize")
            return np.array([], dtype=np.int16)

        try:
            logger.info(f"Synthesizing: '{text[:50]}...'")

            # Use temporary file approach
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp_path = tmp.name

            # Synthesize to file
            self.engine.save_to_file(text, tmp_path)
            self.engine.runAndWait()

            # Read audio file
            try:
                with wave.open(tmp_path, 'rb') as wav_file:
                    n_channels = wav_file.getnchannels()
                    sample_width = wav_file.getsampwidth()
                    framerate = wav_file.getframerate()
                    n_frames = wav_file.getnframes()

                    audio_data = wav_file.readframes(n_frames)
                    audio_array = np.frombuffer(audio_data, dtype=np.int16)

                    if n_channels == 2:
                        # Convert stereo to mono
                        audio_array = audio_array.reshape(-1, 2)
                        audio_array = np.mean(
                            audio_array, axis=1).astype(np.int16)

                    logger.info(
                        f"Synthesis complete: {len(audio_array)} samples at {framerate}Hz")
                    return audio_array

            finally:
                # Clean up temp file
                import os
                try:
                    os.unlink(tmp_path)
                except:
                    pass

        except Exception as e:
            logger.error(f"Error synthesizing text: {e}")
            return np.array([], dtype=np.int16)

    def synthesize_to_file(self, text: str, filepath: str) -> bool:
        """
        Synthesize text and save to WAV file

        Args:
            text: Text to synthesize
            filepath: Output WAV file path

        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return False

        try:
            logger.info(f"Synthesizing to file: {filepath}")
            self.engine.save_to_file(text, filepath)
            self.engine.runAndWait()
            logger.info(f"Saved to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving synthesis to file: {e}")
            return False

    def play(self, text: str) -> bool:
        """
        Synthesize and play text directly

        Args:
            text: Text to synthesize and play

        Returns:
            True if successful, False otherwise
        """
        if not text or not text.strip():
            logger.warning("Empty text provided")
            return False

        try:
            logger.info(f"Playing: '{text[:50]}...'")
            self.engine.say(text)
            self.engine.runAndWait()
            return True

        except Exception as e:
            logger.error(f"Error playing text: {e}")
            return False

    def set_voice(self, voice_index: int) -> bool:
        """
        Set voice by index

        Args:
            voice_index: Index in available voices list

        Returns:
            True if successful
        """
        try:
            if 0 <= voice_index < len(self.voices):
                self.engine.setProperty('voice', self.voices[voice_index].id)
                logger.info(f"Voice set to: {self.voices[voice_index].name}")
                return True
            else:
                logger.warning(f"Voice index {voice_index} out of range")
                return False
        except Exception as e:
            logger.error(f"Error setting voice: {e}")
            return False

    def set_rate(self, rate: int) -> None:
        """Set speech rate in words per minute"""
        try:
            self.rate = rate
            self.engine.setProperty('rate', rate)
            logger.info(f"Rate set to {rate} wpm")
        except Exception as e:
            logger.error(f"Error setting rate: {e}")

    def set_volume(self, volume: float) -> None:
        """
        Set volume level (0.0-1.0)

        Args:
            volume: Volume 0.0 (silent) to 1.0 (max)
        """
        try:
            volume = max(0.0, min(1.0, volume))
            self.volume = volume
            self.engine.setProperty('volume', volume)
            logger.info(f"Volume set to {volume}")
        except Exception as e:
            logger.error(f"Error setting volume: {e}")

    def get_voices(self) -> list:
        """
        Get list of available voices

        Returns:
            List of voice names
        """
        return [v.name for v in self.voices]

    def get_info(self) -> Dict:
        """Get synthesizer configuration info"""
        return {
            "rate": self.rate,
            "volume": self.volume,
            "available_voices": len(self.voices),
            "current_voice": self.voices[0].name if self.voices else "None",
        }

    def stop(self) -> None:
        """Stop current synthesis"""
        try:
            self.engine.stop()
            logger.info("Synthesis stopped")
        except Exception as e:
            logger.error(f"Error stopping synthesis: {e}")

    def __del__(self):
        """Cleanup on deletion"""
        try:
            if hasattr(self, 'engine'):
                self.engine.stop()
        except:
            pass
