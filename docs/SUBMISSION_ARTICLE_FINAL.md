# voicefo: Orchestrating Safe Local AI Agency via Voice

## Introduction
The rapid advancement of Large Language Models (LLMs) has sparked a new frontier in human-computer interaction: Agentic AI. While standard chatbots provide text-based responses, true agents perform tangible actions. **voicefo** is an experimental open-source AI agent designed to bridge the gap between spoken natural language and secure local file system automation. Developed as a high-performance solution for the Mem0 AI Intern Assignment, voicefo prioritizes local-first architecture, system safety, and a transparent execution pipeline.

## The Architecture of voicefo
voicefo is built on a modular "Ear-Brain-Hand" architecture, optimized for low latency and high reliability.

### 1. The Ear: Low-Latency Speech-to-Text
Speech is the most natural interface, but it is also the most prone to hardware-induced latency. voicefo offers a dual-mode STT system:
- **Cloud-Accelerated:** Using Groq's `whisper-large-v3-turbo` API, the system achieves sub-2-second transcription with industrial-grade accuracy.
- **Local-Pure:** Using the `faster-whisper` library, users can opt for a entirely offline experience, ensuring data never leaves the machine.

### 2. The Brain: Structured Planning & Intent
At the heart of voicefo is a custom "Planner-Executor" logic. Unlike simple intent classifiers, voicefo utilizes the `llama-3.1-8b-instant` model to parse transcripts into a structured JSON Execution Plan. This plan includes:
- **Confidence Scoring:** Real-time analysis of the model's certainty.
- **Reasoning Chains:** A transparent explanation of *why* the agent chose a specific path.
- **Ambiguity Detection:** A proactive loop that identifies vague commands (e.g., "create a file") and asks for clarification before acting.

### 3. The Hand: Sandboxed Tool Execution
Safety is the paramount directive. voicefo enforces a rigorous security sandbox:
- **Path Sanitization:** Every file operation is processed via `os.path.basename()` to neutralize directory traversal attacks.
- **Human-in-the-Loop (HITL):** A definitive safety gate where the agent pauses for the user to review, edit, and manually approve the code or file operations before physical disk execution.

## Performance and Real-World Utility
By benchmarking various inference paths, voicefo demonstrates how hybrid-local systems can outperform monolithic local setups. In our tests, switching from CPU-based Whisper to Groq-accelerated STT reduced command-to-execution lag by over 90%, making the agent feel like a real-time partner rather than a slow utility. 

Designed for developers, voicefo handles everything from drafting Python boilerplate to multi-file project scaffolding—all through voice commands. Whether it's creating a complex folder structure or appending a specific function to an existing file, the system maintains context through a persistent session memory.

## Conclusion
voicefo is more than just a voice-controlled application; it is a blueprint for safe, agentic interaction. By combining high-speed inference with strict safety guardrails and a human-centric review process, we demonstrate that AI agents can be both powerful and responsible. As we move toward a world of "Vocal Operating Systems," voicefo stands as a proof-of-concept for the future of developer productivity.

---

**Source Code:** [github.com/pranavsinghpatil/voicefo](https://github.com/pranavsinghpatil/voicefo)  
**Author:** Pranav Singh Patil  
**Project:** Mem0 AI/ML Developer Intern Assignment
