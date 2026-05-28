from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import requests
import os
import json
import subprocess
import re
from pypdf import PdfReader
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
        return f"[Media File '{file.filename}' ready in workspace.]"
    return "[Unsupported File]"

SYSTEM_PROMPT = """You are AutoKaaj OS Agent, an elite autonomous AI Software Engineer.
You have FULL autonomous capability on Termux.
CAPABILITIES: Code, Video/Audio via ffmpeg, Image processing via opencv/Pillow, System commands.
RULE: Wrap ANY terminal commands strictly inside <execute> and </execute> tags."""

@app.post("/api/v1/start-ollama")
async def start_ollama():
    try:
        # আপনার স্পেসিফিক ফ্রি ক্লাউড মডেল রান করার অরিজিনাল মেথড
        # প্রথমে ব্যাকগ্রাউন্ডে সার্ভার স্টার্ট হবে এবং সাথে সাথেই ফ্রি ক্লাউড মডেল টানেলটি অ্যাক্টিভ করবে
        startup_cmd = 'nohup ollama serve > ollama.log 2>&1 & sleep 3 && nohup ollama run gemma4:31b-cloud > auto_cloud.log 2>&1 &'
        subprocess.Popen(startup_cmd, shell=True)
        return {"status": "success", "message": "AutoKaaj Free-Cloud Engine active. Connected to gemma4:31b-cloud without any download!"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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

    # ওলামা লোকাল হোস্টেড রিকোয়েস্ট বা অন্যান্য ক্লাউড হ্যান্ডেল করা
    if provider == "local" or provider == "ollama_cloud":
        endpoint = "http://127.0.0.1:11434/v1/chat/completions"
        try:
            res = requests.post(endpoint, json={"model": model, "messages": msg_list})
            res.raise_for_status()
            reply_text = res.json()["choices"][0]["message"]["content"]
        except Exception as e: raise HTTPException(status_code=500, detail=f"Ollama Cloud Error: {str(e)}")
    elif provider == "gemini":
        if not api_key: raise HTTPException(status_code=400, detail="API Key required")
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        gemini_msg = [{"role": "user" if m["role"] in ["user", "system"] else "model", "parts": [{"text": m["content"]}]} for m in msg_list]
        try:
            res = requests.post(endpoint, headers={"Content-Type": "application/json"}, json={"contents": gemini_msg})
            res.raise_for_status()
            reply_text = res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e: raise HTTPException(status_code=500, detail=f"Gemini Error: {str(e)}")
    else:
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
                action_results += f"\n$ {cmd.strip()}\n[Output]:\n{result[:1000]}\n"
            except Exception as e: action_results += f"\nError executing: {cmd}\n{str(e)}\n"
        reply_text += action_results

    return {"choices": [{"message": {"content": reply_text}}]}

os.makedirs("ui", exist_ok=True)
app.mount("/", StaticFiles(directory="ui", html=True), name="ui")
