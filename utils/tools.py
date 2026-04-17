import os

OUTPUT_DIR = os.path.join(os.getcwd(), "output")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def execute_plan_step(step: dict) -> str:
    action  = step.get("action", "none")
    path    = step.get("path", "")
    content = step.get("content", "")

    if action == "none" or not path:
        return "Skip: No valid action or path defined."

    safe_name = os.path.basename(path)

    if action == "create_folder":
        folder_path = os.path.join(OUTPUT_DIR, safe_name)
        os.makedirs(folder_path, exist_ok=True)
        return f"✅ Created folder `{safe_name}/` in the sandbox."

    filepath = os.path.join(OUTPUT_DIR, safe_name)

    if action in ["create_file", "write_code"]:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"✅ Created `{safe_name}` in the sandbox."

    elif action == "append_code":
        with open(filepath, "a", encoding="utf-8") as f:
            f.write("\n" + content)
        return f"✅ Appended to `{safe_name}` in the sandbox."

    return f"⚠️ Unknown action: {action}"
