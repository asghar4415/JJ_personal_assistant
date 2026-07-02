"""
main.py - JJ application entry point (JARVIS-inspired personalized assistant)

Phase 1: Manual trigger voice chat (no wake word yet)
Workflow: Manual start -> Record/Text -> Transcribe -> Generate -> Speak
"""

from src.utils.logger import setup_logger
from src.core.audio_engine import AudioEngine
from src.core.speech_recognizer import SpeechRecognizer
from src.core.text_synthesizer import TextSynthesizer
from src.core.wake_word_detector import WakeWordDetector
from src.core.voice_activity_detector import VoiceActivityDetector
from src.llm.groq_client import GroqClient
from src.llm.prompt_builder import PromptBuilder
from src.pipeline.query_pipeline import QueryPipeline
from src.pipeline.audio_pipeline import AudioPipeline
from src.config import Config
import sys
import logging
import os
from pathlib import Path

# Setup logging
logger = setup_logger(__name__, log_level=logging.INFO)


class JJApplication:
    """Main JJ application class (JARVIS-inspired)"""

    def __init__(self):
        """Initialize JJ application"""
        logger.info("Initializing JJ Application...")
        self.is_running = False
        self.components = {}
        self.pipeline = None
        self.audio_pipeline = None

    def initialize(self):
        """Initialize all components"""
        logger.info("Setting up Phase 1 components...")

        try:
            # Check for required API key
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                logger.warning("GROQ_API_KEY not set in environment")

            # Initialize AudioEngine
            logger.info("Initializing AudioEngine...")
            self.components["audio"] = AudioEngine(
                sample_rate=Config.SAMPLE_RATE,
                chunk_size=Config.CHUNK_SIZE,
                device=Config.AUDIO_DEVICE,
            )

            # Initialize SpeechRecognizer
            logger.info("Initializing SpeechRecognizer (Whisper)...")
            self.components["speech"] = SpeechRecognizer(
                model_name=Config.WHISPER_MODEL,
                device=Config.WHISPER_DEVICE,
                language=Config.WHISPER_LANGUAGE,
            )

            # Initialize TextSynthesizer
            logger.info("Initializing TextSynthesizer (pyttsx3)...")
            self.components["tts"] = TextSynthesizer(
                rate=150,
                volume=1.0,
            )

            # Initialize GroqClient
            if groq_api_key:
                logger.info("Initializing GroqClient...")
                self.components["llm"] = GroqClient(
                    api_key=groq_api_key,
                    model=Config.GROQ_MODEL,
                    temperature=Config.GROQ_TEMPERATURE,
                    max_tokens=500,
                )
            else:
                logger.error("Cannot initialize GroqClient without API key")
                self.components["llm"] = None

            # Initialize PromptBuilder
            logger.info("Initializing PromptBuilder...")
            self.components["prompt_builder"] = PromptBuilder()

            # Phase 2: Initialize wake word detector and VAD
            logger.info("Initializing WakeWordDetector...")
            self.components["wake"] = WakeWordDetector(
                keyword=Config.WAKE_WORD,
                model_name=Config.WAKE_WORD_MODEL,
                threshold=Config.WAKE_WORD_THRESHOLD,
            )

            logger.info("Initializing VoiceActivityDetector...")
            self.components["vad"] = VoiceActivityDetector(
                silence_seconds=Config.SILENCE_THRESHOLD,
                sample_rate=Config.SAMPLE_RATE,
                chunk_size=Config.CHUNK_SIZE,
            )

            # Initialize QueryPipeline
            if self.components["llm"]:
                logger.info("Initializing QueryPipeline...")
                self.pipeline = QueryPipeline(
                    audio_engine=self.components["audio"],
                    speech_recognizer=self.components["speech"],
                    text_synthesizer=self.components["tts"],
                    groq_client=self.components["llm"],
                    prompt_builder=self.components["prompt_builder"],
                )

                logger.info("Initializing AudioPipeline (Phase 2)...")
                self.audio_pipeline = AudioPipeline(
                    audio_engine=self.components["audio"],
                    wake_word_detector=self.components["wake"],
                    vad=self.components["vad"],
                    query_pipeline=self.pipeline,
                )

            logger.info("All components initialized successfully!")

        except Exception as e:
            logger.error(f"Error during initialization: {e}", exc_info=True)
            self.shutdown()
            raise

    def start(self):
        """Start the application"""
        logger.info("Starting JJ...")
        self.is_running = True
        try:
            self.run()
        except KeyboardInterrupt:
            logger.info("Shutdown requested by user")
            self.shutdown()
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
            self.shutdown()

    def run(self):
        """Main application loop - Phase 1: Manual trigger with text/audio input"""

        if not self.pipeline:
            logger.error("Pipeline not initialized, cannot run")
            self.shutdown()
            return

        print("\n" + "="*60)
        print("JJ - JARVIS-inspired Personal AI Assistant")
        print("="*60)
        print("Phase 1 - Manual Trigger Voice Chat")
        print("\nCommands:")
        print("  [ENTER]       - Record audio query (5 seconds)")
        print("  text query    - Process text query directly")
        print("  info          - Show system info")
        print("  devices       - List audio devices")
        print("  listen        - Start Phase 2 continuous wake-word mode")
        print("  p2status      - Show Phase 2 pipeline status")
        print("  q or quit     - Exit")
        print("="*60 + "\n")

        self.is_running = True

        while self.is_running:
            try:
                user_input = input("\nYou: ").strip()

                # Handle commands
                if user_input.lower() in ['q', 'quit', 'exit']:
                    logger.info("User requested shutdown")
                    self.is_running = False
                    break

                elif user_input.lower() == 'info':
                    self._show_info()
                    continue

                elif user_input.lower() == 'devices':
                    self._show_devices()
                    continue

                elif user_input.lower() == 'listen':
                    self._start_continuous_listening()
                    continue

                elif user_input.lower() == 'p2status':
                    self._show_phase2_status()
                    continue

                elif user_input == '':
                    # Record audio
                    self._process_audio_query()

                else:
                    # Text query
                    self._process_text_query(user_input)

            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                self.is_running = False
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)

    def _process_audio_query(self):
        """Process audio query from microphone"""
        try:
            logger.info("Recording audio query for 5 seconds...")
            print("Recording... speak now!")

            result = self.pipeline.process_query(
                audio_duration=5.0,
                enable_tts=True,
                on_progress=self._progress_callback,
            )

            self._display_result(result)

        except Exception as e:
            logger.error(f"Error processing audio query: {e}")
            print(f"Error: {e}")

    def _process_text_query(self, query: str):
        """Process text query"""
        try:
            logger.info(f"Processing text query: {query}")

            result = self.pipeline.process_text_query(
                text_query=query,
                enable_tts=True,
            )

            self._display_result(result)

        except Exception as e:
            logger.error(f"Error processing text query: {e}")
            print(f"Error: {e}")

    def _progress_callback(self, message: str, percentage: int):
        """Progress callback for pipeline stages"""
        print(f"  [{percentage:3d}%] {message}")

    def _display_result(self, result: dict):
        """Display query result"""
        if not result.get("success", False):
            error_msg = result.get("error", "Unknown error")
            print(f"\nError: {error_msg}")
            return

        query = result.get("user_query", "")
        response = result.get("response", "")
        confidence = result.get("confidence", 0)
        metrics = result.get("metrics", {})

        if query:
            print(f"\nTranscribed: {query}")
            if confidence < 1.0:
                print(f"Confidence: {confidence:.0%}")

        if response:
            print(f"\nJJ: {response}")
        else:
            print("\n(No response)")

        # Show metrics
        if metrics:
            total = metrics.get("total_ms", 0)
            print(f"\nTiming: {total:.0f}ms total")
            if "stt_ms" in metrics:
                print(f"  - STT: {metrics['stt_ms']:.0f}ms")
            if "llm_ms" in metrics:
                print(f"  - LLM: {metrics['llm_ms']:.0f}ms")
            if "tts_ms" in metrics:
                print(f"  - TTS: {metrics['tts_ms']:.0f}ms")
            if "tokens_used" in metrics:
                print(f"  - Tokens: {metrics['tokens_used']}")

    def _show_info(self):
        """Display system information"""
        print("\n" + "="*50)
        print("System Information")
        print("="*50)

        if self.pipeline:
            info = self.pipeline.get_info()

            print("\nAudio Engine:")
            if "audio_engine" in info:
                for k, v in info["audio_engine"].items():
                    print(f"  {k}: {v}")

            print("\nSpeech Recognizer (Whisper):")
            if "speech_recognizer" in info:
                for k, v in info["speech_recognizer"].items():
                    print(f"  {k}: {v}")

            print("\nLLM Client (Groq):")
            if "groq_client" in info:
                for k, v in info["groq_client"].items():
                    print(f"  {k}: {v}")

            print("\nPrompt Builder:")
            if "prompt_builder" in info:
                for k, v in info["prompt_builder"].items():
                    print(f"  {k}: {v}")

    def _show_devices(self):
        """List available audio devices"""
        print("\n" + "="*50)
        print("Audio Devices")
        print("="*50)

        try:
            devices = self.components["audio"].get_devices()
            for device in devices:
                marker = ""
                if device["default_input"]:
                    marker = " [DEFAULT INPUT]"
                elif device["default_output"]:
                    marker = " [DEFAULT OUTPUT]"

                print(f"\n[{device['index']}] {device['name']}{marker}")
                print(
                    f"  In: {device['input_channels']} | Out: {device['output_channels']}")
                print(f"  Sample Rate: {device['sample_rate']}Hz")

        except Exception as e:
            logger.error(f"Error listing devices: {e}")
            print(f"Error: {e}")

    def _start_continuous_listening(self):
        """Start Phase 2 continuous listening loop."""
        if not self.audio_pipeline:
            print("Phase 2 pipeline is not initialized.")
            return

        print("\nStarting Phase 2 continuous listening mode.")
        print("Say wake word to trigger a query. Press Ctrl+C to return to menu.\n")

        def on_event(message: str):
            print(f"[P2] {message}")

        try:
            self.audio_pipeline.start_listening(on_event=on_event)
        except KeyboardInterrupt:
            self.audio_pipeline.stop()
            print("\nExited continuous listening mode.")

    def _show_phase2_status(self):
        """Show Phase 2 component status."""
        print("\n" + "="*50)
        print("Phase 2 Status")
        print("="*50)

        if not self.audio_pipeline:
            print("AudioPipeline: not initialized")
            return

        info = self.audio_pipeline.get_info()
        print(f"Running: {info.get('running')}")
        state = info.get("state", {})
        print(f"State: {state.get('state')} ({state.get('message')})")

        wake = info.get("wake_word", {})
        print("Wake Word Detector:")
        print(f"  enabled: {wake.get('enabled')}")
        print(f"  backend: {wake.get('backend')}")
        print(f"  keyword: {wake.get('keyword')}")

    def shutdown(self):
        """Shutdown the application gracefully"""
        logger.info("Shutting down JJ...")
        self.is_running = False

        # Close components in reverse order
        try:
            if "wake" in self.components and self.components["wake"]:
                logger.info("Closing WakeWordDetector...")
                self.components["wake"].close()

            if "audio" in self.components and self.components["audio"]:
                logger.info("Closing AudioEngine...")
                self.components["audio"].close()
        except Exception as e:
            logger.error(f"Error closing AudioEngine: {e}")

        logger.info("Goodbye!")


def main():
    """Main entry point"""
    app = JJApplication()
    app.initialize()
    app.start()


if __name__ == "__main__":
    main()
