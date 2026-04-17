# voicefo — Local Developer Voice Agent

> *A voice-first AI agent that plans, validates, and safely executes local developer actions from spoken commands.*

**Mem0 AI/ML & Generative AI Developer Intern Assignment Submission**

---

## 🎯 What It Does

voicefo converts a spoken command into a **structured execution plan**, asks you to review and edit it, then writes the output safely into a sandboxed `/output` directory — never touching anything else on your machine.

```
🎙️ Voice Command
      │
      ▼
📝 Speech-to-Text (Groq Whisper / local faster-whisper)
      │
      ▼
🧠 LLM Planner → generates JSON plan with confidence + reasoning
      │
      ▼
🛡️ Safety Validator → path sanitization, injection guard
      │
      ▼
⏸️ Human-in-the-Loop → you review, edit, approve or cancel
      │
      ▼
⚙️ Tool Executor → writes files, code, folders to /output/
      │
      ▼
📦 Artifact Viewer → preview, download, file tree
```

---

## 🧩 Supported Intents

| Intent | Example Command |
|---|---|
| **Write Code** | "Create hello.py that prints Hello World" |
| **Create File** | "Make a config.json with database settings" |
| **Create Folder** | "Create a folder called tests" |
| **Append Code** | "Append a retry decorator to hello.py" |
| **Summarize** | "Summarize: The industrial revolution changed everything" |
| **General Chat** | "What is the difference between a list and a tuple?" |
| **Compound Command** | "Create config.py with settings, and main.py that imports it" |

---

## 🌟 Key Features

- **🔗 Compound Commands** — one voice command triggers multiple file operations
- **⏸️ Human-in-the-Loop** — no file is ever written without your explicit approval
- **✏️ Editable Plan** — every step (filename, action, code) is editable before execution
- **❓ Ambiguity Handling** — vague commands trigger a clarification loop (not silent failure)
- **📊 Confidence + Reasoning** — LLM explains *why* it chose each plan with a confidence score
- **⏱️ Latency Metrics** — STT, LLM, and execution times shown in the UI
- **🕘 Session Memory** — remembers context across commands (e.g. "append to that file")
- **📦 Artifact Viewer** — syntax-highlighted preview + download button per generated file
- **🔒 Safe Sandbox** — all file writes locked to `/output/` via `os.path.basename` enforcement

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit |
| STT (Fast, default) | Groq API → `whisper-large-v3-turbo` |
| STT (Local, opt-in) | `faster-whisper` → `base` model (CPU) |
| LLM (Fast, default) | Groq API → `llama-3.1-8b-instant` |
| LLM (Local, opt-in) | Ollama → configurable model (`qwen3.5`, `llama3`) |
| Tool Executor | Python stdlib (`os`, `pathlib`) |
| Memory | Streamlit `session_state` |
| Safety | `os.path.basename` + LLM injection guard |

---

## 🚀 Setup Instructions

### 1. Prerequisites
- Python 3.9+
- A Groq API key (free at [console.groq.com](https://console.groq.com))
- *(Optional for local LLM)*: [Ollama](https://ollama.com/) installed

### 2. Clone & Install
```bash
git clone <your-repo-url>
cd Voice-agent
pip install -r requirements.txt
```

### 3. Configure Environment
```bash
cp .env.sample .env
```
Edit `.env` and add your Groq API key:
```env
GROQ_API_KEY=your-groq-key-here
USE_LOCAL_STT=false
USE_GROQ_API=true
USE_API_LLM=true
```

### 4. Run
```bash
streamlit run app.py
```
Open `http://localhost:8501`.

---

## 🔒 Hardware Workarounds

### Why Groq API is default (not local Whisper)
The `faster-whisper` library requires **Microsoft Visual C++ Build Tools** to compile on Windows. On machines without it, the `pip install` fails. Additionally, running Whisper's `base` model on a CPU takes **10–20 minutes per clip** — unusable for interactive use.

**Solution**: Groq provides hosted Whisper (`whisper-large-v3-turbo`) via API. Transcription completes in **~1–2 seconds** with higher accuracy than the local `tiny`/`base` models.

To enable local STT (when C++ tools are available):
```env
USE_LOCAL_STT=true
```

### Why Groq LLM is default (not Ollama)
Ollama requires downloading large models (4–7 GB). The `llama3` download failed during development due to TLS timeout on the network. The locally installed `qwen2.5:0.5b` (397 MB) was too small for reliable structured JSON output.

**Solution**: `llama-3.1-8b-instant` on Groq returns structured JSON in **~1 second**. To use local Ollama:
```env
USE_API_LLM=false
LOCAL_LLM_MODEL=qwen3.5:latest
```

---

## 🗂️ Project Structure

```
Voice-agent/
├── app.py                  # Streamlit UI + pipeline orchestration
├── utils/
│   ├── stt.py              # Speech-to-Text (Groq or local faster-whisper)
│   ├── llm.py              # LLM planner (Groq or local Ollama)
│   └── tools.py            # Safe tool executor (sandboxed to /output/)
├── output/                 # ← ALL generated files go here. Nothing else.
├── .env.sample             # Environment variable template
├── .gitignore              # Excludes .env, output/, __pycache__
├── requirements.txt        # Python dependencies
├── PROJECT_FLOW.txt        # Step-by-step system flow documentation
└── LAUNCH_GUIDE.md         # Troubleshooting & manual launch guide
```

---

## 🛡️ Security Architecture

1. **Path Traversal Prevention** — `os.path.basename()` strips any `../../` attempts
2. **Prompt Injection Guard** — System prompt contains a `SECURITY DIRECTIVE` telling the LLM to treat transcripts as data, never as new instructions
3. **Human Approval Gate** — Zero disk writes without explicit user click
4. **API Key Safety** — `.env` is in `.gitignore`; keys never hardcoded

---

## 📎 Deliverables

- [x] GitHub Repository (this repo)
- [ ] Video Demo — YouTube Unlisted (2–3 min)
- [ ] Technical Article — Medium / Dev.to / Substack
