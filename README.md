# Project Jarvis - Personal AI Assistant (JJ)

A fully personalized, always-on AI voice assistant inspired by JARVIS from Iron Man. Unlike generic assistants, Jarvis is built specifically for you with persistent memory that grows smarter with every interaction.

## 🎯 Vision

An intelligent companion that:
- 🎤 Activates with "Hey Jarvis" (no button press)
- 🧠 Remembers your projects, preferences, and context
- ⚡ Responds in <3 seconds
- 🔒 Keeps all personal data local
- 💰 Costs virtually nothing to run

---

## 📚 Documentation

### Core Architecture Files

1. **[ARCHITECTURE.md](./ARCHITECTURE.md)** - System Design
   - High-level system overview with diagrams
   - Audio pipeline flow
   - Memory architecture (3-layer system)
   - Component interactions
   - Data flow cycles
   - Latency budgets and performance targets
   - Security & privacy model
   - Migration path to mini PC

2. **[DATABASE_SCHEMA.md](./DATABASE_SCHEMA.md)** - Memory Layer Design
   - Complete SQLite schema
   - Table designs with full fields
   - Relationships and constraints
   - Common query patterns
   - Archival strategy
   - Performance optimization tips

3. **[MODULE_STRUCTURE.md](./MODULE_STRUCTURE.md)** - Code Organization
   - Project directory layout
   - Module responsibilities and class designs
   - Data models
   - Dependency graph
   - Implementation priority (Phases 1-4)
   - Testing strategy
   - Configuration structure

---

## 🏗️ Project Structure

```
jj_assistant/
├── README.md                      # This file
├── ARCHITECTURE.md                # System design & diagrams
├── DATABASE_SCHEMA.md             # Memory layer schema
├── MODULE_STRUCTURE.md            # Code organization
│
├── src/
│   ├── main.py                    # Entry point
│   ├── config.py                  # Configuration
│   ├── core/                      # Audio I/O, STT, TTS
│   ├── llm/                       # LLM integration
│   ├── memory/                    # SQLite & memory ops
│   ├── pipeline/                  # Audio & query pipelines
│   ├── models/                    # Data classes
│   └── utils/                     # Utilities
│
├── data/
│   ├── user_profile.json          # User profile
│   ├── system_prompt_base.txt     # Base prompt
│   └── jarvis_memory.db           # SQLite DB
│
├── config/
│   ├── default.yaml
│   ├── development.yaml
│   └── production.yaml
│
├── tests/
│   └── test_*.py
│
└── requirements.txt
```

---

## 🛠️ Technology Stack

| Component | Technology | Cost |
|-----------|-----------|------|
| Wake Word | Porcupine (Picovoice) | Free tier |
| Speech-to-Text | OpenAI Whisper | Free (local) |
| LLM | Groq API (Llama 3.1 8B) | Free tier |
| Memory | SQLite | Free |
| TTS | pyttsx3 | Free |
| TTS Premium | ElevenLabs | $5/mo optional |
| Language | Python 3.11+ | Free |

---

## 🚀 Development Phases

### Phase 1 (Week 1-2): Core Voice Loop
- [ ] Set up Python environment
- [ ] Audio I/O with PyAudio
- [ ] Whisper STT integration
- [ ] Groq API integration
- [ ] Basic TTS with pyttsx3
- [ ] Manual trigger voice chat

### Phase 2 (Week 2-3): Wake Word Integration
- [ ] Porcupine wake word setup
- [ ] Always-listening background thread
- [ ] Voice Activity Detection (VAD)
- [ ] Hands-free end-to-end activation

### Phase 3 (Week 3-4): Memory Layer
- [ ] SQLite database schema
- [ ] User profile JSON
- [ ] Context retrieval system
- [ ] Entity extraction
- [ ] Conversation storage

### Phase 4 (Week 4-5): Hardening & Polish
- [ ] Error handling
- [ ] CLI dashboard for memory management
- [ ] Voice commands for memory control
- [ ] Latency optimization
- [ ] Testing & documentation

### Phase 5 (Future): Mini PC Deployment
- [ ] Intel N100 mini PC setup
- [ ] Ubuntu deployment
- [ ] Optional: Local Ollama for zero API cost
- [ ] 24/7 always-on deployment

---

## 💾 Memory Architecture

Three-layer personalization system:

```
Static Profile (JSON)
    ↓ (loaded once per session)
Episodic Memory (SQLite - past conversations)
    ↓ (retrieved for context)
Real-Time Context (in-memory cache)
    ↓ (injected into system prompt)
LLM Response
```

Every query includes:
- Your background and projects
- Last 10 relevant conversations
- Key facts about active tasks
- Your communication preferences
- Current date/time

---

## ⚡ Performance Targets

| Metric | Target | Notes |
|--------|--------|-------|
| Wake word latency | ~50ms | Continuous detection |
| Audio capture | 1-2s | Until speech ends |
| Whisper STT | ~1-1.5s | tiny.en model on CPU |
| LLM inference | 500-800ms | Groq API (200+ tokens/sec) |
| TTS synthesis | 500-1000ms | pyttsx3 |
| **Total E2E** | **<3 seconds** | Wake word to spoken response |

---

## 🔒 Privacy & Security

- ✅ All audio processing local (Porcupine, Whisper)
- ✅ All memory stored locally (SQLite)
- ✅ Only LLM query text sent to Groq API
- ✅ No personal data to external services
- ✅ Optional: Switch to local Ollama for complete privacy

---

## 📋 Quick Start (Roadmap)

1. **Clone and Setup**
   ```bash
   cd jj_assistant
   pip install -r requirements.txt
   ```

2. **Configure**
   ```bash
   cp .env.example .env
   # Add your API keys: PICOVOICE_ACCESS_KEY, GROQ_API_KEY
   ```

3. **Initialize Database**
   ```bash
   python src/main.py --init-db
   ```

4. **Run**
   ```bash
   python src/main.py
   # Say "Hey Jarvis, hello!"
   ```

---

## 🔄 System Flow

```
1. Listening
   ↓ (Porcupine always-on detection)
2. "Hey Jarvis" detected
   ↓ (trigger record)
3. Recording audio
   ↓ (until silence detected by VAD)
4. Transcribe with Whisper
   ↓ (convert speech to text)
5. Build context-rich prompt
   ↓ (retrieve memory, profile, history)
6. Send to Groq LLM
   ↓ (fast inference)
7. Extract entities from response
   ↓ (parse new facts)
8. Convert to speech
   ↓ (TTS synthesis)
9. Play response
   ↓ (speaker output)
10. Store in memory
    ↓ (update SQLite)
11. Return to listening
    ↓ (loop)
```

---

## 📝 Configuration

See `config/default.yaml` for all configurable options:
- Porcupine sensitivity
- Whisper model size
- Groq temperature & tokens
- TTS engine
- Memory settings
- Logging level

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test module
pytest tests/test_memory.py -v

# Run with coverage
pytest --cov=src tests/
```

---

## 🐛 Troubleshooting

### Microphone Issues
- Check audio device: `python -c "import sounddevice; sounddevice.query_devices()"`
- Adjust sensitivity in config

### Wake Word Not Triggering
- Ensure Porcupine access key is set
- Increase sensitivity parameter
- Test with `python -c "from src.core.wake_word_detector import *"`

### Groq API Rate Limited
- Check daily quota (14,400 requests free)
- Implement request queuing
- Fallback to local Ollama

---

## 🗺️ Future Roadmap

### Short-term (Post Phase 4)
- Calendar integration
- Proactive reminders
- WhatsApp/Telegram bridge
- Spotify/YouTube control

### Medium-term (Mini PC Era)
- Multi-room support
- Home automation
- Daily briefings
- Screen awareness
- Full local LLM

### Long-term (Stretch)
- Speaker identification
- Multimodal input (camera)
- Agentic task execution
- Mobile companion app
- Fine-tuned personal model

---

## 📚 References

- [Picovoice Porcupine](https://picovoice.ai/platform/porcupine/)
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Groq API](https://console.groq.com)
- [Ollama](https://ollama.ai)
- [silero-vad](https://github.com/snakers4/silero-vad)

---

## 📄 License

Personal project. Feel free to use as reference or starting point for your own assistant.

---

## 👤 Author

Asghar Ali | FAST-NUCES Karachi | B.S. Computer Science 2026

Last Updated: June 22, 2026