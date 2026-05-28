from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json
import subprocess
import re
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AutoKaaj Universal Autonomous Agent")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Agent Configuration
CONFIG = {"default_model": "gemma4:31b-cloud", "provider": "ollama_cloud"}

@app.on_event("startup")
async def startup_event():
    # অ্যাপ খোলার সাথে সাথে অটোমেটিক ফ্রি ক্লাউড টানেল স্টার্ট করা
    subprocess.Popen('nohup ollama serve > ollama.log 2>&1 & sleep 2 && nohup ollama run gemma4:31b-cloud > auto_sync.log 2>&1 &', shell=True)

@app.post("/api/v1/chat")
async def chat_router(
    provider: str = Form("ollama_cloud"), model: str = Form("gemma4:31b-cloud"),
    api_key: str = Form(""), base_url: str = Form("http://127.0.0.1:11434/v1"),
    messages: str = Form("[]")
):
    msg_list = json.loads(messages)
    # যে কোনো API এন্ডিং এবং Universal মডেল হ্যান্ডলিং
    endpoint = base_url.rstrip('/') + '/chat/completions'
    try:
        res = requests.post(endpoint, headers={"Authorization": f"Bearer {api_key}"}, json={"model": model, "messages": msg_list})
        return res.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gateway Error: {str(e)}")

app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
