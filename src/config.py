"""
config.py - Configuration management for JJ (JARVIS-inspired)

Loads configuration from environment variables and YAML files
"""

import os
import yaml
from pathlib import Path
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)

# Load .env file
env_path = Path(__file__).parent.parent / ".env"
if env_path.exists():
    load_dotenv(env_path)


class Config:
    """Application configuration"""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # API Keys (from environment)
    PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")

    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    AUDIO_DEVICE = os.getenv("AUDIO_DEVICE", "default")

    # Porcupine (Wake Word)
    WAKE_WORD = "Hey JJ"
    PORCUPINE_SENSITIVITY = 0.5

    # Whisper (Speech Recognition)
    WHISPER_MODEL = "tiny.en"  # or "base", "small"
    WHISPER_DEVICE = "cpu"      # or "cuda"
    WHISPER_LANGUAGE = "en"

    # Groq (LLM)
    GROQ_MODEL = "llama-3.1-8b-instant"
    GROQ_TEMPERATURE = 0.7
    GROQ_MAX_TOKENS = 500

    # Memory
    DB_PATH = "data/jarvis_memory.db"
    PROFILE_PATH = "data/user_profile.json"
    MAX_HISTORY_WINDOW = 10
    SILENCE_THRESHOLD = 1.0  # seconds

    # TTS
    TTS_ENGINE = "pyttsx3"  # or "elevenlabs"
    TTS_RATE = 150  # words per minute

    # Logging
    LOG_FILE = "logs/jarvis.log"

    @classmethod
    def load_from_yaml(cls, config_file=None):
        """
        Load configuration from YAML file

        Args:
            config_file: Path to YAML config file

        Returns:
            Updated config dict
        """
        if config_file is None:
            env = cls.ENVIRONMENT
            config_file = Path(__file__).parent.parent / f"config/{env}.yaml"

        if config_file.exists():
            with open(config_file, 'r') as f:
                config_data = yaml.safe_load(f) or {}
                for key, value in config_data.items():
                    if hasattr(cls, key.upper()):
                        setattr(cls, key.upper(), value)
                logger.info(f"Loaded configuration from {config_file}")
        else:
            logger.warning(f"Config file not found: {config_file}")

        return cls

    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_keys = ["GROQ_API_KEY"]

        for key in required_keys:
            if not getattr(cls, key, None):
                logger.warning(f"Missing required config: {key}")

        logger.info("Configuration validation complete")


# Initialize on import
Config.load_from_yaml()
