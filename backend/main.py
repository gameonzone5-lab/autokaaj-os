from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json
import subprocess
import re
from pypdf import PdfReader
import base64
import io
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="AutoKaaj OS Core API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

WORKSPACE_DIR = os.path.join(os.getcwd(), "workspace")
os.makedirs(WORKSPACE_DIR, exist_ok=True)

def process_file(file: UploadFile):
    ext = file.filename.split('.')[-1].lower()
    if ext == "pdf":
        reader = PdfReader(file.file)
        return "[PDF Content]:\n" + "".join([page.extract_text() + "\n" for page in reader.pages])
    elif ext in ["jpg", "jpeg", "png", "mp4", "mp3", "wav"]: 
        return f"[Media File '{file.filename}' uploaded. Agent can use ffmpeg/python to process.]"
    return "[Unsupported/Unknown File Uploaded]"

SYSTEM_PROMPT = """You are AutoKaaj OS Agent, an elite autonomous AI Software Engineer.
You have FULL autonomous capability on Termux.
CAPABILITIES: Code, Video/Audio via ffmpeg, Image processing via opencv/Pillow, System commands.
If user asks to pull/run Ollama models manually, use: <execute>proot-distro login debian --shared-tmp -- bash -c "ollama pull MODEL_NAME"</execute>
RULE: Wrap ANY terminal commands strictly inside <execute> and </execute> tags."""

@app.post("/api/v1/start-ollama")
async def start_ollama():
    try:
        # ১. Ollama সার্ভার স্টার্ট করবে
        # ২. ব্যাকগ্রাউন্ডে gemma4:31b-cloud মডেলটি অটোমেটিক pull এবং run করবে
        startup_cmd = 'proot-distro login debian --shared-tmp -- bash -c "nohup ollama serve > ollama.log 2>&1 & sleep 5 && nohup ollama run gemma4:31b-cloud > auto_pull.log 2>&1 &"'
        subprocess.Popen(startup_cmd, shell=True)
        return {"status": "success", "message": "Background Services Started. 'gemma4:31b-cloud' is syncing automatically."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/chat")
async def chat_router(
    provider: str = Form(...), model: str = Form(...), api_key: str = Form(""),
    base_url: str = Form(""), messages: str = Form("[]"), file: UploadFile = File(None)
):
    msg_list = json.loads(messages)
    if not any(m.get("role") == "system" for m in msg_list):
        msg_list.insert(0, {"role": "system", "content": SYSTEM_PROMPT})
    
    if file:
        file_path = os.path.join(WORKSPACE_DIR, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
        msg_list.append({"role": "user", "content": f"File context:\n{process_file(file)}"})
    
    reply_text = ""

    if provider == "gemini":
        if not api_key: raise HTTPException(status_code=400, detail="API Key required")
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        gemini_msg = [{"role": "user" if m["role"] in ["user", "system"] else "model", "parts": [{"text": m["content"]}]} for m in msg_list]
        try:
            res = requests.post(endpoint, headers={"Content-Type": "application/json"}, json={"contents": gemini_msg})
            res.raise_for_status()
            reply_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e: raise HTTPException(status_code=500, detail=f"Gemini Error: {str(e)}")
    else:
        if not base_url: raise HTTPException(status_code=400, detail="Base URL required")
        endpoint = base_url.rstrip('/') + '/chat/completions'
        try:
            res = requests.post(endpoint, headers={"Authorization": f"Bearer {api_key}"}, json={"model": model, "messages": msg_list})
            res.raise_for_status()
            reply_text = res.json()["choices"][0]["message"]["content"]
        except Exception as e: raise HTTPException(status_code=500, detail=f"API Error: {str(e)}")

    execute_matches = re.findall(r"<execute>(.*?)</execute>", reply_text, re.DOTALL)
    if execute_matches:
        action_results = "\n\n[Agent Executed Actions:]\n"
        for cmd in execute_matches:
            try:
                result = subprocess.getoutput(f"cd {WORKSPACE_DIR} && {cmd.strip()}")
                action_results += f"\n$ {cmd.strip()}\n[Output]:\n{result[:1500]}\n"
            except Exception as e: action_results += f"\nError executing: {cmd}\n{str(e)}\n"
        reply_text += action_results

    return {"choices": [{"message": {"content": reply_text}}]}

os.makedirs("ui", exist_ok=True)
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
