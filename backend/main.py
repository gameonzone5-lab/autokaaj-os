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
        return f"[Media File '{file.filename}' uploaded successfully to workspace. You can now process it using ffmpeg, python, or other tools.]"
    return "[Unsupported/Unknown File Uploaded]"

# --- THE ULTIMATE AUTONOMOUS AGENT SYSTEM PROMPT ---
SYSTEM_PROMPT = """You are AutoKaaj OS Agent, an elite autonomous AI Software Engineer and Media Creator, comparable to OpenManus or OpenClaw.
You are running natively on an Android Termux environment. You have FULL autonomous capability.

YOUR CAPABILITIES:
1. CODE & BUILD: You can write Python, HTML, JS, CSS, and build complete games or apps.
2. VIDEO & AUDIO: You have `ffmpeg`, `moviepy`, `pydub`, and `yt-dlp` installed. You can cut, merge, extract, and manipulate video/audio files directly.
3. IMAGES: You have `imagemagick`, `Pillow`, and `opencv-python` to edit, resize, and process images.
4. SYSTEM CONTROL: You can navigate folders, read/write files, and execute bash scripts.

RULE OF EXECUTION:
To perform ANY action (edit a video, write a script, build a game), you MUST write the terminal command or python script inside strict <execute> tags.
Example to write and run a python game:
<execute>
cat << 'PY' > game.py
print("Game Logic Here")
PY
python game.py
</execute>

Example to extract audio from a video:
<execute>ffmpeg -i input.mp4 -q:a 0 -map a output.mp3</execute>

Never say "I cannot do this". Write the script or command in <execute> tags and do it! Think step-by-step like a senior developer."""

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

