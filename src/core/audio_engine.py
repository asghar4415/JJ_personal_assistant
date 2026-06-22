"""
audio_engine.py - Audio I/O wrapper for microphone and speaker

Provides cross-platform audio capture and playback using PyAudio and sounddevice.
Handles microphone input, speaker output, and device management.
"""

import numpy as np
import pyaudio
import sounddevice as sd
import logging
from typing import Generator, Optional, List, Dict

logger = logging.getLogger(__name__)


class AudioEngine:
    """Audio I/O engine for microphone capture and speaker playback"""

    def __init__(self, sample_rate: int = 16000, chunk_size: int = 1024, device: str = "default"):
        """
        Initialize audio engine

        Args:
            sample_rate: Sample rate in Hz (default: 16000)
            chunk_size: Chunk size in samples (default: 1024)
            device: Audio device name or "default"
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device = device
        self.is_recording = False
        
        # Initialize PyAudio
        self.pa = pyaudio.PyAudio()
        logger.info(f"AudioEngine initialized: {sample_rate}Hz, chunk_size={chunk_size}")

    def get_devices(self) -> List[Dict]:
        """
        Get list of available audio devices

        Returns:
            List of device dictionaries with name, index, channels, sample_rate
        """
        devices = []
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            device_info = {
                "index": i,
                "name": info["name"],
                "input_channels": info["maxInputChannels"],
                "output_channels": info["maxOutputChannels"],
                "sample_rate": int(info["defaultSampleRate"]),
                "default_input": i == self.pa.get_default_input_device(),
                "default_output": i == self.pa.get_default_output_device(),
            }
            devices.append(device_info)
        return devices

    def stream_audio(self, duration: Optional[float] = None) -> Generator[np.ndarray, None, None]:
        """
        Stream audio from microphone

        Yields numpy arrays of audio frames (int16) of specified chunk_size.
        Run as: for frame in audio_engine.stream_audio():
                    # process frame

        Args:
            duration: Recording duration in seconds (None = continuous)

        Yields:
            numpy arrays of audio frames (dtype: int16)
        """
        try:
            # Find device index
            device_index = self._get_device_index()
            
            logger.info(f"Opening input stream: device={device_index}, rate={self.sample_rate}, chunk={self.chunk_size}")
            
            # Open microphone stream
            stream = self.pa.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=self.chunk_size,
                exceptions=False,
            )

            self.is_recording = True
            frames_read = 0
            max_frames = int(self.sample_rate / self.chunk_size * duration) if duration else None

            while self.is_recording:
                try:
                    data = stream.read(self.chunk_size, exception_on_overflow=False)
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    frames_read += 1
                    
                    yield audio_data
                    
                    # Check duration limit
                    if max_frames and frames_read >= max_frames:
                        break
                        
                except Exception as e:
                    logger.error(f"Error reading audio frame: {e}")
                    break

            stream.stop_stream()
            stream.close()
            logger.info(f"Recording stopped after {frames_read} frames")
            self.is_recording = False

        except Exception as e:
            logger.error(f"Error in stream_audio: {e}")
            self.is_recording = False
            raise

    def play_audio(self, audio_data: np.ndarray) -> None:
        """
        Play audio through speaker

        Args:
            audio_data: numpy array of audio samples (float32 or int16)
        """
        try:
            # Validate input
            if not isinstance(audio_data, np.ndarray):
                raise ValueError("audio_data must be numpy array")
            
            if len(audio_data) == 0:
                logger.warning("Empty audio data, skipping playback")
                return
            
            # Ensure int16 format
            if audio_data.dtype != np.int16:
                # Normalize float32 to int16
                if audio_data.dtype in [np.float32, np.float64]:
                    audio_data = np.clip(audio_data * 32767, -32768, 32767).astype(np.int16)
                else:
                    audio_data = audio_data.astype(np.int16)
            
            logger.info(f"Playing {len(audio_data)} samples at {self.sample_rate}Hz")
            
            # Use sounddevice for playback (better cross-platform support)
            sd.play(audio_data, samplerate=self.sample_rate, device=self.device)
            sd.wait()  # Wait for playback to finish
            
        except Exception as e:
            logger.error(f"Error playing audio: {e}")
            raise

    def record_to_file(self, filename: str, duration: float) -> None:
        """
        Record audio to WAV file

        Args:
            filename: Output filename (e.g., "output.wav")
            duration: Recording duration in seconds
        """
        try:
            import wave
            
            logger.info(f"Recording {duration}s to {filename}")
            
            frames = []
            for frame in self.stream_audio(duration=duration):
                frames.append(frame)
            
            if not frames:
                logger.warning("No audio recorded")
                return
            
            # Combine frames
            audio_data = np.concatenate(frames)
            
            # Write to WAV file
            with wave.open(filename, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 2 bytes for int16
                wav_file.setframerate(self.sample_rate)
                wav_file.writeframes(audio_data.tobytes())
            
            logger.info(f"Audio saved to {filename}")
            
        except Exception as e:
            logger.error(f"Error recording to file: {e}")
            raise

    def stop_recording(self) -> None:
        """Stop the current recording stream"""
        self.is_recording = False
        logger.info("Recording stop signal sent")

    def _get_device_index(self) -> Optional[int]:
        """
        Get device index by name or return default

        Returns:
            Device index or None for default
        """
        if self.device == "default":
            return None
        
        # Search for device by name
        for i in range(self.pa.get_device_count()):
            info = self.pa.get_device_info_by_index(i)
            if self.device.lower() in info["name"].lower():
                logger.info(f"Found device '{self.device}' at index {i}")
                return i
        
        logger.warning(f"Device '{self.device}' not found, using default")
        return None

    def close(self) -> None:
        """Close audio engine and release resources"""
        try:
            self.is_recording = False
            self.pa.terminate()
            logger.info("AudioEngine closed")
        except Exception as e:
            logger.error(f"Error closing AudioEngine: {e}")

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()

    def get_info(self) -> Dict:
        """Get engine configuration info"""
        return {
            "sample_rate": self.sample_rate,
            "chunk_size": self.chunk_size,
            "device": self.device,
            "is_recording": self.is_recording,
            "total_devices": self.pa.get_device_count(),
        }
