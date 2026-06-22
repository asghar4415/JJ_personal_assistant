# Quick Start Guide - JJ Assistant

## Setup

### 1. Set Groq API Key (Required for full functionality)

Get your free API key from: **https://console.groq.com**

**On Windows PowerShell:**
```powershell
$env:GROQ_API_KEY = 'gsk_your_api_key_here'
```

**On Windows Command Prompt:**
```cmd
set GROQ_API_KEY=gsk_your_api_key_here
```

**On Linux/Mac:**
```bash
export GROQ_API_KEY='gsk_your_api_key_here'
```

To make it permanent, add to your environment variables or `.env` file.

### 2. Run JJ Assistant

```bash
cd JJ_personal_assistant
python run_jj.py
```

## Usage

Once running, JJ presents an interactive menu:

```
JJ - JARVIS-inspired Personal AI Assistant
==================================================
Phase 1 - Manual Trigger Voice Chat

Commands:
  [ENTER]       - Record audio query (5 seconds)
  text query    - Process text query directly
  info          - Show system info
  devices       - List audio devices
  q or quit     - Exit
```

### Examples:

**Record audio:**
```
You: [Press ENTER]
Recording... speak now!
```

**Send text query:**
```
You: What is my current project deadline?
JJ: Based on your profile, your FYP deadline is June 20, 2026...
```

**View system info:**
```
You: info
[displays audio engine, whisper, groq, and prompt builder info]
```

**List audio devices:**
```
You: devices
[shows available microphones and speakers]
```

## Architecture - Phase 1 Components

| Component | Module | Purpose |
|-----------|--------|---------|
| **AudioEngine** | `src/core/audio_engine.py` | Microphone I/O and speaker playback |
| **SpeechRecognizer** | `src/core/speech_recognizer.py` | Speech-to-text (Whisper) |
| **TextSynthesizer** | `src/core/text_synthesizer.py` | Text-to-speech (pyttsx3) |
| **GroqClient** | `src/llm/groq_client.py` | LLM API integration |
| **PromptBuilder** | `src/llm/prompt_builder.py` | Context + memory management |
| **QueryPipeline** | `src/pipeline/query_pipeline.py` | End-to-end orchestration |

## Configuration

### Audio Settings
Edit `config/default.yaml`:
```yaml
audio:
  sample_rate: 16000      # Hz
  chunk_size: 1024        # samples
  device: "default"       # or specify device index

whisper:
  model: "tiny.en"        # tiny.en, base, small
  device: "cpu"           # cpu or cuda
  language: "en"

groq:
  model: "llama-3.1-8b-instant"
  temperature: 0.7        # 0.0-2.0
  max_tokens: 500
```

## Environment Variables

Create a `.env` file with:
```
GROQ_API_KEY=gsk_your_api_key_here
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO
```

## Troubleshooting

### "No audio captured"
- Check microphone is connected
- Try `devices` command to list audio devices
- On Windows, check Sound Settings

### "Empty transcription"
- Speak louder/clearer
- Move closer to microphone
- Check audio device settings

### "GROQ_API_KEY not set"
- Follow setup instructions above
- Verify key is active at console.groq.com
- Restart terminal after setting env variable

### pyttsx3 warning at shutdown
- This is normal on Windows (pyttsx3 cleanup issue)
- Does not affect functionality

## Logs

Application logs are saved to:
```
logs/jj.log
```

## Next Steps (Phase 2+)

- [ ] Wake word detection ("Hey JJ")
- [ ] Voice Activity Detection (VAD)
- [ ] Continuous listening loop
- [ ] Memory persistence (SQLite)
- [ ] Entity extraction and tagging
- [ ] Multi-turn conversation context
- [ ] Custom voice selection
- [ ] Integration with user calendars/notes

---

**GitHub:** https://github.com/asghar4415/JJ_Assistant  
**Status:** Phase 1 - Manual Trigger Voice Chat ✓
