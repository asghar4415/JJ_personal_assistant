"""
constants.py - Application-wide constants and enumerations
"""

# Audio settings
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_CHUNK_SIZE = 1024

# Model names
WHISPER_MODEL_TINY = "tiny.en"
WHISPER_MODEL_BASE = "base"
GROQ_MODEL_DEFAULT = "llama-3.1-8b-instant"

# Timeouts (in seconds)
AUDIO_TIMEOUT = 30
LLM_TIMEOUT = 30
DATABASE_TIMEOUT = 5

# Memory settings
DEFAULT_MAX_HISTORY = 10
DEFAULT_SILENCE_THRESHOLD = 1.0  # seconds

# Response settings
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500

# Confidence thresholds
STT_CONFIDENCE_THRESHOLD = 0.6
ENTITY_CONFIDENCE_THRESHOLD = 0.5

# Entity types
ENTITY_TYPES = {
    "PROJECT": "project",
    "PERSON": "person",
    "DATE": "date",
    "PREFERENCE": "preference",
    "GOAL": "goal",
    "TOOL": "tool",
    "CONCEPT": "concept",
}

# Session states
SESSION_STATES = {
    "LISTENING": "listening",
    "RECORDING": "recording",
    "PROCESSING": "processing",
    "RESPONDING": "responding",
    "ERROR": "error",
}
