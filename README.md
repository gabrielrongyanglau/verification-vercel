# Venting GPT — Starter (Beginner Friendly)

This is the tiniest possible starter to run a supportive, non-clinical “venting” bot **locally** using the OpenAI API.

## 0) Prerequisites
- Python 3.10+ (https://www.python.org/downloads/)
- An OpenAI API key (create at https://platform.openai.com/ — Dashboard → API keys)

## 1) Download & open this folder
Unzip `venting-gpt-starter.zip`, then open a terminal **in that folder**.

## 2) Create a virtual environment (recommended)
**macOS/Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
```
**Windows (PowerShell)**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

## 3) Install dependencies
```bash
pip install -r requirements.txt
```

## 4) Add your API key
Copy `.env.example` to `.env` and paste your key after `OPENAI_API_KEY=`.

> Tip: Never hardcode keys into your code. Keep `.env` out of version control.

## 5) Run the bot
```bash
python main.py
```
Type a message and press Enter. Type `quit` to exit.

## 6) Change the bot’s personality
Edit `system_prompt.txt`. Keep it short and clear. The current prompt is designed for a supportive listener, not a therapist.

## 7) Safety
This starter uses OpenAI’s free moderation endpoint to pre-check user inputs. In a production app, you should:
- Show a short consent notice (do not share PII; this is not therapy).
- Add a crisis-response fallback and store minimal logs.
- Pin the model (`model="gpt-5"`) and settings for reproducibility.

## 8) Troubleshooting
- **ModuleNotFoundError: openai** → Run `pip install -r requirements.txt` inside your **activated** venv.
- **Invalid API key** → Regenerate a key in the dashboard and update `.env`.
- **Rate limit** → Wait a bit or reduce message length.
- **Firewall/Proxy** → Ensure outbound HTTPS (TCP 443) is allowed.

---

### What’s next?
- Wrap this in a simple web server (FastAPI) and connect a UI.
- Add streaming for more responsive typing.
- Keep a short chat history (we already trim) to control costs.
