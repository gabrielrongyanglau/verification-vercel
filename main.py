#!/usr/bin/env python3
"""
Minimal "Venting GPT" you can run in your terminal.

New:
  - Type `export_chat_history` at any time to save all user/assistant turns into a CSV named chat_history_YYYY-MM-DD_HHMM.csv in the current folder.

Setup:
  1) Copy .env.example to .env and paste your API key.
  2) pip install -r requirements.txt
  3) python main.py
"""

import os
import csv
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI()

# Load system prompt from file (edit to taste)
with open("system_prompt.txt", "r", encoding="utf-8") as f:
    SYSTEM = f.read().strip()

def moderate(text: str) -> bool:
    """
    Returns True if content is flagged by OpenAI's free moderation endpoint.
    """
    try:
        res = client.moderations.create(
            model="omni-moderation-latest",
            input=text
        )
        return bool(getattr(res.results[0], "flagged", False))
    except Exception:
        # If the moderation call fails, fail open but keep a small safeguard
        return False

def respond(history):
    """
    Calls the Responses API with the conversation history.
    """
    try:
        resp = client.responses.create(
            model="gpt-4o-mini",
            input=history,
            temperature=1.0,
            max_output_tokens=200
        )
        return resp.output_text.strip()
    except Exception as e:
        return f"(Error talking to the model: {e})"

# --- NEW ---
def export_chat_history(history) -> str:
    """
    Exports all user and assistant messages in chronological order to CSV.
    Excludes the system prompt. Returns the file path.
    Columns:
      order: absolute order across the conversation (starts at 1)
      pair: conversational pair index (user/assistant ≈ same pair number)
      role: 'user' or 'assistant'
      message: text content
      timestamp: export time (same for all rows in this export)
    """
    # Filter out only user/assistant messages
    convo = [h for h in history if h.get("role") in {"user", "assistant"}]

    ts = datetime.now().strftime("%Y-%m-%d_%H%M")
    filename = f"chat_history_{ts}.csv"
    export_time_iso = datetime.now().isoformat(timespec="seconds")

    # Compute pair index assuming the conversation alternates user→assistant
    rows = []
    for idx, msg in enumerate(convo, start=1):
        pair = (idx + 1) // 2  # 1,1,2,2,3,3,...
        rows.append({
            "order": idx,
            "pair": pair,
            "role": msg.get("role", ""),
            "message": msg.get("content", ""),
            "timestamp": export_time_iso
        })

    # Write CSV (UTF-8 with newline handling across OSes)
    with open(filename, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["order", "pair", "role", "message", "timestamp"])
        writer.writeheader()
        writer.writerows(rows)

    return filename
# --- NEW ---

def main():
    print("Venting GPT (type 'quit' to exit)\n")
    history = [
        {"role": "system", "content": SYSTEM}
    ]

    while True:
        user = input("You: ").strip()
        if not user:
            continue

        # --- NEW: export command (handled before moderation/model calls) ---
        if user.lower() == "export_chat_history":
            path = export_chat_history(history)
            print(f"Gabriel: Chat history exported to {path}\n")
            continue
        # -------------------------------------------------------------------

        if user.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break

        # Pre-moderate
        if moderate(user):
            print("Gabriel: I hear you. I’m not able to go into that safely. "
                  "If you’re in immediate danger, please contact local emergency services. "
                  "If you’d like, I can share professional resources.\n")
            # We do not add sensitive content to history
            continue

        history.append({"role": "user", "content": user})
        assistant = respond(history)
        print(f"Gabriel: {assistant}\n")
        history.append({"role": "assistant", "content": assistant})

        # Keep the last few turns to save tokens
        if len(history) > 13:
            # retain system + last 6 exchanges (12 entries)
            history = [history[0]] + history[-12:]

# Making the bot into the terminal
if __name__ == "__main__":
    main()
