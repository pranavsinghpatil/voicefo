# VoiceForge - Local Developer Voice Agent

A voice-first AI agent that plans, validates, and safely executes local developer actions from spoken commands.

Mem0 AI/ML & Generative AI Developer Intern Assignment Submission

---

## What It Does

VoiceForge converts a spoken command into a structured execution plan, asks you to review and edit it, then writes the output safely into a sandboxed `/output` directory.

```
Voice Command
      |
      v
Speech-to-Text (Groq Whisper / local faster-whisper)
      |
      v
LLM Planner  -->  JSON plan with confidence + reasoning
      |
      v
Safety Validator  -->  path sanitization, injection guard
      |
      v
Human-in-the-Loop  -->  review, edit, approve or cancel
      |
      v
Tool Executor  -->  writes files, code, folders to /output/
      |
      v
Artifact Viewer  -->  preview, download, file tree
```

---

## Supported Intents

| Intent | Example Command |
|---|---|
| Write Code | "Create hello.py that prints Hello World" |
| Create File | "Make a config.json with database settings" |
| Create Folder | "Create a folder called tests" |
| Append Code | "Append a retry decorator to hello.py" |
| Summarize | "Summarize: The industrial revolution changed everything" |
| General Chat | "What is the difference between a list and a tuple?" |
| Compound Command | "Create config.py with settings, and main.py that imports it" |

---

## Key Features

- Compound Commands: one voice command triggers multiple file operations
- Human-in-the-Loop: no file is ever written without explicit user approval
- Editable Plan: every step (filename, action, code) is editable before execution
- Ambiguity Handling: vague commands trigger a clarification loop, not silent failure
- Confidence + Reasoning: LLM explains why it chose each plan with a confidence score
- Latency Metrics: STT, LLM, and execution times shown in the UI
- Session Memory: remembers context across commands within a session
- Artifact Viewer: syntax-highlighted preview and download button per generated file
- Safe Sandbox: all file writes locked to `/output/` via `os.path.basename` enforcement

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit |
| STT (Fast, default) | Groq API - whisper-large-v3-turbo |
| STT (Local, opt-in) | faster-whisper - base model on CPU |
| LLM (Fast, default) | Groq API - llama-3.1-8b-instant |
| LLM (Local, opt-in) | Ollama - configurable model (qwen3.5, llama3) |
| Tool Executor | Python stdlib (os, pathlib) |
| Memory | Streamlit session_state |
| Safety | os.path.basename + LLM injection guard |

---

## Setup Instructions

### Prerequisites
- Python 3.9+
- A Groq API key (free at https://console.groq.com)
- Optional for local LLM: Ollama installed (https://ollama.com)

### Install
```bash
git clone https://github.com/pranavsinghpatil/voicefo.git
cd voicefo
pip install -r requirements.txt
```

### Configure
```bash
cp .env.sample .env
```

Edit `.env` and add your Groq API key:
```
GROQ_API_KEY=your-groq-key-here
USE_LOCAL_STT=false
USE_GROQ_API=true
USE_API_LLM=true
```

### Run
```bash
streamlit run app.py
```

Open `http://localhost:8501`.

---

## Hardware Workarounds

### Why Groq API is default for STT

The `faster-whisper` library requires Microsoft Visual C++ Build Tools to compile on Windows. On machines without it, installation fails. Running Whisper's `base` model on CPU also takes 10-20 minutes per audio clip, which is unusable for interactive use.

Groq provides hosted Whisper (`whisper-large-v3-turbo`) via API. Transcription completes in 1-2 seconds with higher accuracy than local tiny/base models.

To enable local STT when C++ build tools are available:
```
USE_LOCAL_STT=true
```

### Why Groq API is default for LLM

Ollama requires downloading large models (4-7 GB). The llama3 download failed during development due to TLS timeouts. The locally installed qwen2.5:0.5b was too small for reliable structured JSON output.

`llama-3.1-8b-instant` on Groq returns structured JSON in under 1 second.

To use local Ollama:
```
USE_API_LLM=false
LOCAL_LLM_MODEL=qwen3.5:latest
```

---

## Project Structure

```
voiceforge/
├── app.py                  # Streamlit UI and pipeline orchestration
├── utils/
│   ├── stt.py              # Speech-to-Text (Groq or local faster-whisper)
│   ├── llm.py              # LLM planner (Groq or local Ollama)
│   └── tools.py            # Safe tool executor (sandboxed to /output/)
├── output/                 # All generated files go here. Nothing else.
├── .env.sample             # Environment variable template
├── .gitignore              # Excludes .env, output/, __pycache__
├── requirements.txt        # Python dependencies
├── PROJECT_FLOW.txt        # Step-by-step system flow documentation
└── LAUNCH_GUIDE.md         # Troubleshooting and manual launch guide
```

---

## Security Architecture

1. Path Traversal Prevention: `os.path.basename()` strips any `../../` attempts
2. Prompt Injection Guard: system prompt contains a SECURITY DIRECTIVE telling the LLM to treat transcripts as data, not instructions
3. Human Approval Gate: zero disk writes without explicit user click
4. API Key Safety: `.env` is in `.gitignore`; keys are never hardcoded

---

## Deliverables

- [x] GitHub Repository
- [ ] Video Demo - YouTube Unlisted (2-3 min)
- [ ] Technical Article - Medium / Dev.to / Substack
