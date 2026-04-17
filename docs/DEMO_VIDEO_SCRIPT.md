# 🎬 voicefo: Demo Video Script (2-3 Minutes)

This script is designed to show the reviewer that **voicefo** is a robust, intelligent agent, not just a simple voice wrapper.

---

## **Part 1: Introduction (0:00 - 0:20)**
**Visual:** Show the `voicefo` UI in the browser.
**Audio:** "Hi, I'm Pranav, and this is **voicefo**—a safe, local-first voice agent built for developers. Unlike simple voice classifiers, voicefo uses a Planner-Executor architecture to understand, validate, and execute complex local file operations."

---

## **Part 2: Scenario 1 - Code Generation & Human-in-the-Loop (0:20 - 1:00)**
**Action:** Click the mic and speak the command.
**Command:** *"Create a python file called hello.py that runs a loop 10 times and prints the current iteration."*

**What to show:**
1. Point to the **Execution Trace** as it updates (STT -> Planning -> Safety).
2. Point to the **Confidence Score** and the **Reasoning** bullets.
3. Show the **Editable Plan**. Click inside the code area to show you *could* change it.
4. Click **"Approve and Execute"**.
5. Show the **Artifact Preview** at the bottom with the highlighted code.

**Audio:** "First, I'll ask voicefo to generate some Python code. Notice the system doesn't just execute blindly. It builds a structured plan, shows its reasoning, and waits for my approval. This 'Human-in-the-Loop' gate ensures total control over my local directory."

---

## **Part 3: Scenario 2 - Handling Ambiguity (1:00 - 1:40)**
**Action:** Record a vague command.
**Command:** *"I want to create a file."*

**What to show:**
1. The UI will show **"Ambiguity Detected"** in bright red/orange.
2. Show the **Clarification Questions** the agent asks.
3. Type into the clarification box: *"Create a text file named notes.txt with the content 'Meeting at 5 PM'"* and hit Enter.
4. Show the new plan being generated and approved.

**Audio:** "A key feature of voicefo is how it handles uncertainty. When I give a vague command, the agent refuses to guess. Instead, it flags the ambiguity and asks specific clarification questions to gather the missing metadata, like filenames or file types."

---

## **Part 4: Scenario 3 - Compound Commands & Memory (1:40 - 2:30)**
**Action:** Record a multi-step command related to the first file.
**Command:** *"Create a folder called scripts, and then append a function called 'done' to hello.py that prints 'Execution finished'."*

**What to show:**
1. The plan shows **multiple steps** (Step 1: Create Folder, Step 2: Append Code).
2. Note that it remembered `hello.py` existed from earlier (Memory).
3. Approve and show the updated file tree in the sidebar/bottom.

**Audio:** "Finally, voicefo supports compound commands and session memory. I can ask it to perform multiple actions across different tools in a single breath. Because it tracks our conversation history, it knows exactly which file I'm referring to when I ask to append new logic."

---

## **Part 5: Conclusion (2:30 - Ends)**
**Visual:** Show the `/output` folder on your computer (containing the files) and the final UI state.
**Audio:** "Everything you've seen runs with low-latency via Groq-accelerated inference while maintaining a strictly local-first safety sandbox. That’s voicefo. Thanks for watching."

---

## **Quick Checklist for Recording:**
1. **Reset First**: Click "Clear Session" before you start.
2. **Speak Clearly**: Wait 0.5s after clicking 'Record' before speaking.
3. **Show the Metrics**: Briefly highlight the "Latency Metrics" box to show it's fast.
4. **Output Folder**: Keep the `output/` folder open in your file explorer on the side so people can see the files appearing "live".
