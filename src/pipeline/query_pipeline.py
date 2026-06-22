"""
query_pipeline.py - Voice query processing pipeline

Orchestrates the complete voice query flow:
Audio Capture → Transcription → Prompt Building → LLM Generation → Text-to-Speech
"""

import logging
import time
from typing import Dict, Optional, Callable
import numpy as np

logger = logging.getLogger(__name__)


class QueryPipeline:
    """Orchestrates voice query processing pipeline"""

    def __init__(
        self,
        audio_engine,
        speech_recognizer,
        text_synthesizer,
        groq_client,
        prompt_builder,
    ):
        """
        Initialize query pipeline with all components

        Args:
            audio_engine: AudioEngine instance for mic/speaker I/O
            speech_recognizer: SpeechRecognizer instance for STT
            text_synthesizer: TextSynthesizer instance for TTS
            groq_client: GroqClient instance for LLM
            prompt_builder: PromptBuilder instance for context
        """
        self.audio_engine = audio_engine
        self.speech_recognizer = speech_recognizer
        self.text_synthesizer = text_synthesizer
        self.groq_client = groq_client
        self.prompt_builder = prompt_builder

        # Configuration
        self.enable_tts = True
        self.confidence_threshold = 0.5

        logger.info("QueryPipeline initialized")

    def process_query(
        self,
        user_input: Optional[str] = None,
        audio_duration: float = 5.0,
        enable_tts: bool = True,
        on_progress: Optional[Callable] = None,
    ) -> Dict:
        """
        Process voice query end-to-end

        Args:
            user_input: Optional pre-transcribed text (skips STT)
            audio_duration: Recording duration in seconds (default: 5)
            enable_tts: Whether to play response via TTS (default: True)
            on_progress: Callback function for progress updates

        Returns:
            Dictionary with keys:
            - "user_query": Transcribed or provided query
            - "response": Generated response text
            - "confidence": Speech recognition confidence
            - "metrics": Timing metrics for each stage
            - "success": Whether query succeeded
        """
        start_time = time.time()
        metrics = {}

        try:
            # Stage 1: Audio Capture (if not using pre-transcribed input)
            user_query = None
            confidence = 1.0

            if user_input is None:
                # Capture audio
                self._progress(on_progress, "Recording audio...", 10)

                audio_start = time.time()
                audio_frames = []

                logger.info(f"Recording for {audio_duration}s...")
                for frame in self.audio_engine.stream_audio(duration=audio_duration):
                    audio_frames.append(frame)

                if not audio_frames:
                    logger.warning("No audio captured")
                    return {
                        "user_query": "",
                        "response": "",
                        "confidence": 0.0,
                        "metrics": {"total_ms": (time.time() - start_time) * 1000},
                        "success": False,
                        "error": "No audio captured",
                    }

                audio_data = np.concatenate(audio_frames)
                metrics["audio_capture_ms"] = (
                    time.time() - audio_start) * 1000

                # Stage 2: Speech Recognition (STT)
                self._progress(on_progress, "Transcribing speech...", 30)

                stt_start = time.time()
                transcription = self.speech_recognizer.transcribe(
                    audio_data,
                    sample_rate=self.audio_engine.sample_rate
                )

                user_query = transcription.get("text", "").strip()
                confidence = transcription.get("confidence", 0.0)
                metrics["stt_ms"] = (time.time() - stt_start) * 1000

                logger.info(
                    f"Transcribed: '{user_query}' (conf: {confidence:.2f})")

                if not user_query:
                    logger.warning("Empty transcription")
                    return {
                        "user_query": "",
                        "response": "",
                        "confidence": confidence,
                        "metrics": metrics,
                        "success": False,
                        "error": "Failed to transcribe audio",
                    }

                # Check confidence threshold
                if confidence < self.confidence_threshold:
                    logger.warning(f"Low confidence: {confidence:.2f}")
            else:
                # Use provided input
                user_query = user_input.strip()
                logger.info(f"Using provided input: '{user_query}'")

            # Stage 3: Update prompt builder with new query
            self._progress(on_progress, "Building context...", 50)

            context_start = time.time()
            self.prompt_builder.add_to_history("user", user_query)
            system_prompt = self.prompt_builder.build_prompt()
            metrics["context_build_ms"] = (time.time() - context_start) * 1000

            # Stage 4: Generate LLM Response
            self._progress(on_progress, "Generating response...", 60)

            llm_start = time.time()
            llm_result = self.groq_client.generate_response(
                system_prompt=system_prompt,
                user_query=user_query,
            )

            response_text = llm_result.get("content", "")
            metrics["llm_ms"] = llm_result.get("latency_ms", 0)
            metrics["tokens_used"] = llm_result.get("tokens_used", 0)

            logger.info(f"Generated response: {len(response_text)} chars")

            if not response_text:
                logger.warning("Empty LLM response")
            else:
                # Add to history
                self.prompt_builder.add_to_history("assistant", response_text)

            # Stage 5: Text-to-Speech (optional)
            if enable_tts and response_text:
                self._progress(on_progress, "Synthesizing speech...", 80)

                tts_start = time.time()
                try:
                    audio_output = self.text_synthesizer.synthesize(
                        response_text)

                    if len(audio_output) > 0:
                        # Play audio
                        self._progress(on_progress, "Playing response...", 90)
                        self.audio_engine.play_audio(audio_output)

                    metrics["tts_ms"] = (time.time() - tts_start) * 1000
                except Exception as e:
                    logger.error(f"TTS error: {e}")
                    metrics["tts_ms"] = (time.time() - tts_start) * 1000
                    metrics["tts_error"] = str(e)

            # Calculate total latency
            metrics["total_ms"] = (time.time() - start_time) * 1000

            self._progress(on_progress, "Complete", 100)

            logger.info(
                f"Query processed successfully in {metrics['total_ms']:.0f}ms")

            return {
                "user_query": user_query,
                "response": response_text,
                "confidence": confidence,
                "metrics": metrics,
                "success": True,
                "llm_finish_reason": llm_result.get("finish_reason", "unknown"),
            }

        except Exception as e:
            logger.error(f"Error in query pipeline: {e}", exc_info=True)
            metrics["total_ms"] = (time.time() - start_time) * 1000

            return {
                "user_query": "",
                "response": "",
                "confidence": 0.0,
                "metrics": metrics,
                "success": False,
                "error": str(e),
            }

    def process_text_query(self, text_query: str, enable_tts: bool = True) -> Dict:
        """
        Process text query (skip audio capture and STT)

        Args:
            text_query: Text input query
            enable_tts: Whether to play response

        Returns:
            Result dictionary (see process_query)
        """
        return self.process_query(
            user_input=text_query,
            enable_tts=enable_tts,
        )

    def set_confidence_threshold(self, threshold: float) -> None:
        """
        Set minimum STT confidence threshold

        Args:
            threshold: Confidence threshold (0.0-1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, threshold))
        logger.info(f"Confidence threshold set to {self.confidence_threshold}")

    def get_info(self) -> Dict:
        """Get pipeline information and statistics"""
        return {
            "audio_engine": self.audio_engine.get_info(),
            "speech_recognizer": self.speech_recognizer.get_info(),
            "groq_client": self.groq_client.get_info(),
            "prompt_builder": self.prompt_builder.get_info(),
            "confidence_threshold": self.confidence_threshold,
        }

    def _progress(
        self,
        callback: Optional[Callable],
        message: str,
        percentage: int,
    ) -> None:
        """
        Call progress callback if provided

        Args:
            callback: Callback function
            message: Progress message
            percentage: Progress percentage (0-100)
        """
        if callback:
            try:
                callback(message, percentage)
            except Exception as e:
                logger.error(f"Error in progress callback: {e}")
