import json
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from llmgeneration import llmanswer
from pydantic import BaseModel


class ChatRequest(BaseModel):
    query: str
    session_id: Optional[str] = "guest"


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/')
def home():
    return {"message": "Server is running"}


@app.post('/ask')
async def ask_suryaprakash(payload: ChatRequest, req: Request):
    # Extract real visitor IP (supports Cloudflare Tunnel & standard proxies)
    client_ip = (
        req.headers.get("cf-connecting-ip")
        or req.headers.get("x-forwarded-for", "").split(",")[0].strip()
        or (req.client.host if req.client else "unknown")
    )

    try:
        response = llmanswer(payload.query)

        # Structured CloudWatch Log (automatically indexed by AWS)
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_ip": client_ip,
            "session_id": payload.session_id,
            "user_query": payload.query,
            "bot_response": response,
            "status": "success",
        }
        print(json.dumps(log_entry), flush=True)

        return {"message": f"{response}"}

    except Exception as e:
        import traceback
        traceback.print_exc()

        # Structured error log
        error_log = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "client_ip": client_ip,
            "session_id": payload.session_id,
            "user_query": payload.query,
            "error": str(e),
            "status": "failed",
        }
        print(json.dumps(error_log), flush=True)

        if "429" in str(e) or "RESOURCE_EXHAUSTED" in str(e):
            return {"message": "The assistant is receiving many requests right now. Please wait a few seconds and try again!"}
        return {"message": f"Error: {str(e)}"}
