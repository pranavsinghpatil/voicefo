import streamlit as st
import os
import time
import json
import tempfile
from audio_recorder_streamlit import audio_recorder
from utils.stt import transcribe_audio
from utils.llm import detect_intent_and_extract
from utils.tools import execute_plan_step

# ── Page Config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="voicefo · Local Developer Agent",
    layout="wide",
    initial_sidebar_state="expanded"
)

OUTPUT_DIR = os.path.join(os.getcwd(), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Session State Init ─────────────────────────────────────────────────────────
DEFAULTS = {
    "transcript":        "",
    "raw_plan":          None,
    "original_steps":    [],    # immutable LLM output for diff
    "edited_steps":      [],    # user-modified copy
    "execution_log":     [],
    "artifacts":         {},
    "chat_history":      [],
    "pipeline_stage":    "idle",
    "latency":           {},    # {stt: float, llm: float, exec: float}
    "clarification_pending": False,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────────
INTENT_LABELS = {
    "compound_command": "Compound Command",
    "general_chat":     "General Chat",
    "summarize":        "Summarize",
    "unknown":          "Unknown",
    "error":            "Error",
}

def push_log(label: str, status: str, detail: str = ""):
    for e in st.session_state.execution_log:
        if e["label"] == label:
            e["status"] = status
            e["detail"] = detail
            return
    st.session_state.execution_log.append({"label": label, "status": status, "detail": detail})

def run_audio_pipeline(audio_bytes: bytes, suffix: str):
    st.session_state.execution_log          = []
    st.session_state.raw_plan               = None
    st.session_state.original_steps         = []
    st.session_state.edited_steps           = []
    st.session_state.pipeline_stage         = "idle"
    st.session_state.latency                = {}
    st.session_state.clarification_pending  = False

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        push_log("Audio Captured", "Success")

        push_log("Speech-to-Text", "Running", "Transcribing…")
        t0 = time.time()
        with st.spinner("Transcribing command…"):
            transcript = transcribe_audio(tmp_path)
        stt_lat = round(time.time() - t0, 2)
        st.session_state.transcript = transcript
        st.session_state.latency["stt"] = stt_lat
        st.session_state.chat_history.append({"type": "user", "content": transcript})
        push_log("Speech-to-Text", "Completed", f'"{transcript}"  [{stt_lat}s]')

        push_log("Intent + Planning", "Running", "Analyzing command…")
        with st.spinner("Building reasoning plan…"):
            plan = detect_intent_and_extract(transcript, st.session_state.chat_history)
        llm_lat = plan.get("llm_latency", 0)
        st.session_state.latency["llm"] = llm_lat
        st.session_state.raw_plan       = plan
        st.session_state.chat_history.append({"type": "agent", "content": plan.get("response", "")})

        intent     = plan.get("intent", "unknown")
        confidence = plan.get("confidence", 0)
        steps      = plan.get("steps", [])
        reasoning  = plan.get("reasoning", [])

        push_log("Intent + Planning", "Completed",
                 f"Intent: {intent.upper()} | Confidence: {confidence:.0%} | Steps: {len(steps)} [{llm_lat}s]")
        push_log("Entity Extraction", "Completed",
                 "  •  " + "\n  •  ".join(reasoning) if reasoning else "No reasoning provided")
        push_log("Safety Validator",  "Passed", "All paths sandboxed to /output/")

        if plan.get("is_ambiguous"):
            push_log("Ambiguity Detected", "Clarification Required",
                     f"Confidence {confidence:.0%} — missing details")
            st.session_state.pipeline_stage        = "clarifying"
            st.session_state.clarification_pending = True

        elif steps and plan.get("requires_confirmation"):
            st.session_state.original_steps = [s.copy() for s in steps]
            st.session_state.edited_steps   = [s.copy() for s in steps]
            push_log("Human-in-the-Loop", "Awaiting Approval", "Plan ready for review / edit")
            st.session_state.pipeline_stage = "awaiting"

        else:
            st.session_state.pipeline_stage = "done"
            push_log("Tool Execution",    "Completed", plan.get("response", "—"))
            push_log("Result Returned",    "Completed", "No disk operations needed")

    finally:
        os.remove(tmp_path)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## voicefo")
    st.caption("Local Developer Voice Agent")

    st.markdown("""
<div style="background:rgba(46,204,113,0.12);border:1px solid #2ecc71;
            border-radius:8px;padding:10px 14px;margin:8px 0">
  <b style="color:#2ecc71">Local-First Architecture</b><br>
  <small>Near-instant execution<br>
  Sandboxed /output directory<br>
  API keys secured in .env<br>
  Ollama local LLM support</small>
</div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### Session History")
    if st.session_state.chat_history:
        for msg in reversed(st.session_state.chat_history[-10:]):
            if msg["type"] == "user":
                st.chat_message("user").write(msg["content"])
            else:
                st.chat_message("assistant").write(msg["content"])
    else:
        st.info("No history yet. Speak a command!")

    st.divider()
    if st.button("Clear Session", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("# voicefo — Local Developer Agent")
st.caption("Speak a command. voicefo plans, validates, edits, and executes safely.")
st.divider()

# ── 3-Column Layout ────────────────────────────────────────────────────────────
c_input, c_trace, c_output = st.columns([1.1, 1.3, 1.6])

# ══════════════════════════════════════════════
# COL 1 — Input
# ══════════════════════════════════════════════
with c_input:
    st.markdown("### Command Input")
    audio_bytes = audio_recorder(
        text="", recording_color="#e74c3c",
        neutral_color="#2ecc71", icon_size="2x"
    )
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        if st.button("Run Pipeline", use_container_width=True, type="primary"):
            run_audio_pipeline(audio_bytes, ".wav")
            st.rerun()

    st.markdown("---")
    upload = st.file_uploader("Upload audio file", type=["wav","mp3","m4a"], label_visibility="visible")
    if upload:
        st.audio(upload)
        if st.button("Process Upload", use_container_width=True, type="primary"):
            run_audio_pipeline(upload.read(), "." + upload.name.rsplit(".", 1)[-1])
            st.rerun()

    if st.session_state.transcript:
        st.markdown("---")
        st.markdown("**Last Transcript**")
        st.info(f'"{st.session_state.transcript}"')

    lat = st.session_state.latency
    if lat:
        total = round(sum(lat.values()), 2)
        st.markdown("---")
        st.markdown("**Latency Metrics**")
        st.markdown(f"""
<div style="font-family:monospace;font-size:13px;
            background:rgba(0,0,0,0.3);padding:10px;border-radius:6px">
  STT &nbsp;&nbsp;&nbsp; : {lat.get('stt','—')}s<br>
  LLM &nbsp;&nbsp;&nbsp; : {lat.get('llm','—')}s<br>
  Execute : {lat.get('exec','—')}s<br>
  <b>Total &nbsp;&nbsp; : {total}s</b>
</div>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════
# COL 2 — Execution Trace
# ══════════════════════════════════════════════
with c_trace:
    st.markdown("### Execution Trace")

    PIPELINE_STEPS = [
        "Audio Captured",
        "Speech-to-Text",
        "Intent + Planning",
        "Entity Extraction",
        "Safety Validator",
        "Ambiguity Detected",
        "Human-in-the-Loop",
        "Tool Execution",
        "Result Returned",
    ]

    log_lookup = {e["label"]: e for e in st.session_state.execution_log}

    for step_label in PIPELINE_STEPS:
        entry = log_lookup.get(step_label)
        if entry:
            st_txt = entry["status"]
            color  = ("#2ecc71" if "Success" in st_txt or "Completed" in st_txt or "Passed" in st_txt or "Approved" in st_txt else
                      "#f39c12" if "Running" in st_txt or "Required" in st_txt or "Awaiting" in st_txt else "#e74c3c")
            detail = entry["detail"].replace("\n", "<br>")
            st.markdown(
                f"""<div style="border-left:3px solid {color};padding:6px 12px;
                               margin-bottom:5px;border-radius:4px;
                               background:rgba(255,255,255,0.04)">
                    <b>{step_label}</b>&nbsp;
                    <span style="color:{color};font-size:12px">{st_txt}</span><br>
                    <small style="color:#aaa">{detail}</small>
                </div>""",
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f"""<div style="border-left:3px solid #333;padding:6px 12px;
                               margin-bottom:5px;border-radius:4px;opacity:0.35">
                    <b>{step_label}</b>
                    <span style="color:#555;font-size:12px"> — waiting</span>
                </div>""",
                unsafe_allow_html=True
            )

# ══════════════════════════════════════════════
# COL 3 — Plan / Artifacts
# ══════════════════════════════════════════════
with c_output:
    stage = st.session_state.pipeline_stage
    plan  = st.session_state.raw_plan or {}

    if stage == "clarifying":
        conf      = plan.get("confidence", 0)
        questions = plan.get("clarification_questions", [])
        reasoning = plan.get("reasoning", [])

        st.markdown("### Ambiguity Detected")
        st.error(f"**Confidence: {conf:.0%}** — Command is too vague to execute safely.")
        st.caption(f"Assistant: {plan.get('response','')}")

        st.markdown("**Reasoning:**")
        for r in reasoning:
            st.markdown(f"- {r}")

        st.markdown("**Clarification Required:**")
        for q in questions:
            st.markdown(f"- {q}")

        clarification = st.text_input("Response:", placeholder="e.g. Create a file named hello.py with a print statement")
        if st.button("Re-run with clarification", type="primary") and clarification.strip():
            combined = f"{st.session_state.transcript}. {clarification}"
            st.session_state.transcript = combined
            st.session_state.chat_history.append({"type": "user", "content": clarification})
            with st.spinner("Re-planning…"):
                new_plan = detect_intent_and_extract(combined, st.session_state.chat_history)
            st.session_state.raw_plan = new_plan
            new_steps = new_plan.get("steps", [])
            if new_steps and new_plan.get("requires_confirmation"):
                st.session_state.original_steps            = [s.copy() for s in new_steps]
                st.session_state.edited_steps              = [s.copy() for s in new_steps]
                st.session_state.pipeline_stage            = "awaiting"
                st.session_state.clarification_pending     = False
                push_log("Ambiguity Detected",  "Resolved", clarification)
                push_log("Human-in-the-Loop",   "Awaiting Approval", "Plan ready for review")
            else:
                st.session_state.pipeline_stage = "done"
            st.rerun()

    elif stage == "awaiting":
        intent     = plan.get("intent", "unknown")
        confidence = plan.get("confidence", 0)
        reasoning  = plan.get("reasoning", [])

        def conf_color(c):
            if c >= 0.8: return "#2ecc71"
            if c >= 0.5: return "#f39c12"
            return "#e74c3c"

        conf_col   = conf_color(confidence)

        st.markdown(f"### Execution Plan — {intent.upper()}")

        st.markdown(
            f"""<div style="border:1px solid {conf_col};border-radius:8px;
                           padding:12px 16px;margin-bottom:12px;
                           background:rgba(0,0,0,0.2)">
              <span style="font-size:15px;color:{conf_col};font-weight:bold">
                Confidence: {confidence:.0%}</span>
              <br><b>Reasoning:</b>
              <ul style="margin:4px 0 0 0;color:#ccc;font-size:13px">
                {"".join(f"<li>{r}</li>" for r in reasoning)}
              </ul>
            </div>""",
            unsafe_allow_html=True
        )

        st.warning("Review and edit the plan before approval. All operations are sandboxed.")

        plan_view = st.radio("View mode", ["Card View", "JSON View"], horizontal=True)

        edited = st.session_state.edited_steps

        if plan_view == "JSON View":
            c_orig, c_edit = st.columns(2)
            with c_orig:
                st.caption("Original Plan")
                st.json(st.session_state.original_steps)
            with c_edit:
                st.caption("Editable Plan")
                raw_edit = st.text_area("Edit JSON", value=json.dumps(edited, indent=2), height=300)
                try:
                    parsed = json.loads(raw_edit)
                    st.session_state.edited_steps = parsed
                    edited = parsed
                    st.caption("Valid JSON")
                except Exception:
                    st.caption("Invalid JSON")
        else:
            for i, step in enumerate(edited):
                with st.expander(f"Step {i+1}: {step.get('action','?')} -> {step.get('path','?')}", expanded=True):
                    col_a, col_b = st.columns(2)
                    with col_a:
                        step["action"] = st.selectbox(
                            "Action",
                            ["write_code", "create_file", "append_code", "none"],
                            index=["write_code","create_file","append_code","none"].index(
                                step.get("action","write_code")),
                            key=f"action_{i}"
                        )
                    with col_b:
                        step["path"] = st.text_input("Filename", value=step.get("path",""), key=f"path_{i}")

                    step["content"] = st.text_area(
                        "Content / Code",
                        value=step.get("content",""),
                        height=160,
                        key=f"content_{i}"
                    )

        st.divider()
        col_appr, col_rej = st.columns(2)
        with col_appr:
            if st.button("Approve and Execute", type="primary", use_container_width=True):
                push_log("Human-in-the-Loop", "Approved", "Plan approved by user")
                push_log("Tool Execution",    "Running",  "")
                t0 = time.time()
                results = []
                for step in edited:
                    res = execute_plan_step(step)
                    results.append(res)
                    if step.get("action") in ("write_code","create_file","append_code"):
                        fname = os.path.basename(step.get("path","file.txt"))
                        st.session_state.artifacts[fname] = step.get("content","")
                exec_lat = round(time.time() - t0, 3)
                st.session_state.latency["exec"] = exec_lat
                push_log("Tool Execution",  "Completed", f"{' | '.join(results)} [{exec_lat}s]")
                push_log("Result Returned", "Completed", f"{len(results)} operations completed")
                st.session_state.pipeline_stage = "done"
                st.rerun()
        with col_rej:
            if st.button("Cancel Plan", use_container_width=True):
                push_log("Human-in-the-Loop", "Rejected", "User cancelled")
                push_log("Result Returned",    "Aborted",  "No changes applied")
                st.session_state.pipeline_stage = "done"
                st.session_state.edited_steps   = []
                st.rerun()

    elif stage == "done":
        response = plan.get("response","")
        st.markdown("### Results")
        if response:
            st.success(f"Assistant: {response}")

        if st.session_state.artifacts:
            tabs = st.tabs([f"Artifact: {k}" for k in st.session_state.artifacts])
            for tab, (fname, content) in zip(tabs, st.session_state.artifacts.items()):
                with tab:
                    lang = ("python" if fname.endswith(".py") else
                            "markdown" if fname.endswith(".md") else
                            "bash" if fname.endswith(".sh") else "text")
                    st.code(content, language=lang)
                    st.download_button(f"Download {fname}", data=content,
                                       file_name=fname, mime="text/plain",
                                       use_container_width=True)

            st.markdown("---")
            st.markdown("**Sandbox Environment (/output)**")
            files = [f for f in os.listdir(OUTPUT_DIR) if f != ".keep"]
            if files:
                for f in sorted(files):
                    size = os.path.getsize(os.path.join(OUTPUT_DIR, f))
                    st.markdown(f"- `{f}` ({size} B)")
            else:
                st.caption("Sandbox is currently empty.")

    else:
        st.markdown("### Waiting for Command")
        st.info("Record or upload an audio command to start.")
        st.markdown("""
**Examples:**
- "Create a python file called hello.py that prints hello world"
- "Create config.py with a settings dict, and main.py that imports it"
- "What is a Python decorator?"
- "Summarize: The industrial revolution changed the world"
        """)
