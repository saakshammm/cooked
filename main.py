# main.py
# fastapi server, loads .env for local NVIDIA NIM key

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, File, UploadFile, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from local_analyzer import LocalChatAnalyzer
from nim_analyzer import NIMChatAnalyzer

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

INDEX_HTML = Path("templates/index.html").read_text(encoding="utf-8")

@app.get("/", response_class=HTMLResponse)
async def get_index():
    return HTMLResponse(content=INDEX_HTML)

@app.post("/analyze")
async def analyze_chat(file: UploadFile = File(...),
                       chat_type: str = Form("direct"),
                       user_id: str = Form(None)):
    content = await file.read()
    if not content:
        return JSONResponse(status_code=400, content={"error": "empty file"})

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        text = content.decode("latin-1", errors="replace")

    api_key = os.getenv("NVIDIA_API_KEY")
    if api_key:
        analyzer = NIMChatAnalyzer(text, chat_type, user_id, api_key)
    else:
        analyzer = LocalChatAnalyzer(text, chat_type, user_id)

    result = await analyzer.run_analysis()
    return JSONResponse(content=result)