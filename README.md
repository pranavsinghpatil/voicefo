# voicefo - Local Developer Voice Agent

A voice-first AI agent that plans, validates, and safely executes local developer actions from spoken commands.

**Mem0 AI/ML & Generative AI Developer Intern Assignment Submission**

---

## Deliverables

- **Demo Video:** [Link to Video](INSERT_YOUR_YOUTUBE_LINK_HERE)
- **Technical Article:** [Link to Article](INSERT_YOUR_ARTICLE_LINK_HERE)
- **Source Code:** [github.com/pranavsinghpatil/voicefo](https://github.com/pranavsinghpatil/voicefo)

---

## What It Does

voicefo converts a spoken command into a structured execution plan, asks the user to review and edit it, then writes the output safely into a sandboxed `/output` directory.

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

## Key Features

- **Compound Commands**: Trigger multiple file operations with a single voice command.
- **Human-in-the-Loop**: No file is ever written without explicit user approval via an editable review stage.
- **Ambiguity Handling**: Proactively identifies vague commands and asks clarifying questions.
- **Transparency**: Highlighting confidence scores and reasoning bullets for every decision.
- **Safety**: Strict path-traversal protection and sandboxed execution in `/output`.

---

## Tech Stack

| Layer | Technology |
|---|---|
| UI Framework | Streamlit |
| STT | Groq API (whisper-large-v3-turbo) |
| LLM | Groq API (llama-3.1-8b-instant) |
| Tool Layer | Python standard libraries (os, pathlib) |
| Safety | Path sanitization + HITL validation |

---

## Setup & Configuration

1. **Clone and Install**:
   ```bash
   git clone https://github.com/pranavsinghpatil/voicefo.git
   cd voicefo
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.sample` to `.env` and add your Groq API key:
   ```env
   GROQ_API_KEY=your-api-key-here
   USE_GROQ_API=true
   USE_API_LLM=true
   ```

3. **Run**:
   ```bash
   streamlit run app.py
   ```

---

## Project Structure

```
voicefo/
├── app.py                  # Streamlit UI & Pipeline Orchestration
├── utils/
│   ├── stt.py              # Speech-to-Text routing
│   ├── llm.py              # Intent planning & reasoning
│   └── tools.py            # Local tool execution
├── docs/                   # Documentation, flows, and scripts
├── output/                 # Sandboxed file output directory
├── requirements.txt        # Project dependencies
└── .env.sample             # Environment configuration template
```

---

## Safety & Security

- **Path Sanitization**: Enrollment of `os.path.basename()` on all user-supplied filenames to prevent directory traversal attacks.
- **Prompt Guard**: System-level directives to prevent prompt injection and unauthorized command execution.
- **Validation Gate**: A mandatory manual approval step for all physical file system mutations.
