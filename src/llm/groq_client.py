"""
groq_client.py - Groq LLM API Client

Provides interface to Groq API for text generation with Llama models.
"""

import logging
import time
from typing import Dict, Optional
from groq import Groq

logger = logging.getLogger(__name__)


class GroqClient:
    """Groq LLM API client for text generation"""

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.1-8b-instant",
        temperature: float = 0.7,
        max_tokens: int = 500,
    ):
        """
        Initialize Groq client

        Args:
            api_key: Groq API key
            model: Model name (default: llama-3.1-8b-instant)
            temperature: Temperature for generation (0.0-2.0, default: 0.7)
            max_tokens: Maximum tokens in response (default: 500)
        """
        self.api_key = api_key
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Validate API key
        if not api_key:
            raise ValueError("Groq API key is required")

        logger.info(
            f"Initializing Groq client: model={model}, temp={temperature}, max_tokens={max_tokens}")

        try:
            self.client = Groq(api_key=api_key)
            logger.info("Groq client initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing Groq client: {e}")
            raise

    def generate_response(
        self,
        system_prompt: str,
        user_query: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> Dict:
        """
        Generate response from LLM

        Args:
            system_prompt: System context/instructions
            user_query: User query/prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Returns:
            Dictionary with keys:
            - "content": Generated response text
            - "tokens_used": Total tokens used (input + output)
            - "latency_ms": Response time in milliseconds
            - "model": Model used
            - "finish_reason": How generation ended ("stop", "length", etc.)
        """
        if not user_query or not user_query.strip():
            logger.warning("Empty user query")
            return {
                "content": "",
                "tokens_used": 0,
                "latency_ms": 0,
                "model": self.model,
                "finish_reason": "empty_query",
            }

        try:
            temp = temperature if temperature is not None else self.temperature
            max_tk = max_tokens if max_tokens is not None else self.max_tokens

            logger.info(
                f"Generating response: temp={temp}, max_tokens={max_tk}")
            logger.debug(f"System: {system_prompt[:100]}...")
            logger.debug(f"Query: {user_query[:100]}...")

            start_time = time.time()

            # Call Groq API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                temperature=temp,
                max_tokens=max_tk,
                top_p=0.95,
                stream=False,
            )

            latency_ms = (time.time() - start_time) * 1000

            # Extract response
            content = response.choices[0].message.content.strip()
            tokens_used = response.usage.total_tokens
            finish_reason = response.choices[0].finish_reason

            result = {
                "content": content,
                "tokens_used": tokens_used,
                "latency_ms": latency_ms,
                "model": self.model,
                "finish_reason": finish_reason,
            }

            logger.info(
                f"Response generated: {len(content)} chars, {tokens_used} tokens, {latency_ms:.0f}ms")
            return result

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "content": "",
                "tokens_used": 0,
                "latency_ms": 0,
                "model": self.model,
                "finish_reason": "error",
                "error": str(e),
            }

    def generate_response_stream(
        self,
        system_prompt: str,
        user_query: str,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ):
        """
        Generate response with streaming

        Yields response chunks as they arrive from the API.

        Args:
            system_prompt: System context/instructions
            user_query: User query/prompt
            temperature: Override default temperature
            max_tokens: Override default max_tokens

        Yields:
            Response text chunks
        """
        if not user_query or not user_query.strip():
            logger.warning("Empty user query")
            return

        try:
            temp = temperature if temperature is not None else self.temperature
            max_tk = max_tokens if max_tokens is not None else self.max_tokens

            logger.info("Generating streaming response")

            # Call Groq API with streaming
            stream = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query},
                ],
                temperature=temp,
                max_tokens=max_tk,
                stream=True,
            )

            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content

        except Exception as e:
            logger.error(f"Error in streaming generation: {e}")

    def set_model(self, model: str) -> None:
        """Change the model"""
        self.model = model
        logger.info(f"Model changed to {model}")

    def set_temperature(self, temperature: float) -> None:
        """Set default temperature"""
        self.temperature = max(0.0, min(2.0, temperature))
        logger.info(f"Temperature set to {self.temperature}")

    def set_max_tokens(self, max_tokens: int) -> None:
        """Set default max tokens"""
        self.max_tokens = max(1, max_tokens)
        logger.info(f"Max tokens set to {self.max_tokens}")

    def get_info(self) -> Dict:
        """Get client configuration info"""
        return {
            "model": self.model,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
