import logging
import os
from collections import defaultdict

from openai import OpenAI
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

SYSTEM_PROMPT = (
    "Ты голосовой ассистент. Отвечай кратко и разговорно, "
    "без списков и маркдауна. Максимум 2-3 предложения."
)

# session_id -> list of {"role": ..., "content": ...}
sessions: dict[str, list[dict]] = defaultdict(list)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/gpt")
async def alice_webhook(request: Request):
    body = await request.json()

    session = body.get("session", {})
    session_id: str = session.get("session_id", "")
    is_new: bool = session.get("new", False)
    request_body = body.get("request", {})
    utterance: str = request_body.get("original_utterance", "").strip()
    version: str = body.get("version", "1.0")

    logger.info("session_id=%s new=%s utterance=%r", session_id, is_new, utterance)

    if is_new:
        sessions[session_id] = []

    if not utterance:
        reply_text = "Привет! Я Chat GPT, я слушаю."
    else:
        sessions[session_id].append({"role": "user", "content": utterance})

        try:
            messages = [{"role": "system", "content": SYSTEM_PROMPT}] + sessions[session_id]
            response = client.chat.completions.create(
                model="gpt-5.4",
                max_tokens=500,
                messages=messages,
            )
            reply_text = response.choices[0].message.content.strip()
            sessions[session_id].append({"role": "assistant", "content": reply_text})
            logger.info("openai reply for session %s: %r", session_id, reply_text)
        except Exception as exc:
            logger.error("OpenAI API error: %s", exc)
            reply_text = "Произошла ошибка, попробуй ещё раз."

    return JSONResponse(
        content={
            "version": version,
            "session": session,
            "response": {
                "text": reply_text,
                "tts": reply_text,
                "end_session": False,
            },
        }
    )
