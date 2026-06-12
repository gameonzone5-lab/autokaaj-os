import subprocess
import os
import threading
import time
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# EXTENDED AGENT REGISTRY WITH OLLAMA ENGINE
# ==========================================
AGENT_REGISTRY = {
    "openmanus": (
        "git clone https://github.com/mannaandpoem/OpenManus.git || true && "
        "cd OpenManus && pip3 install -r requirements.txt --break-system-packages --ignore-installed"
    ),
    "openclaw": (
        "git clone https://github.com/OpenClaw/OpenClaw.git || true && "
        "cd OpenClaw && pip3 install -r requirements.txt --break-system-packages --ignore-installed"
    ),
    "claudecode": (
        "npm install -g @anthropic-ai/claude-code"
    ),
    "aider": (
        "pip3 install --upgrade pip setuptools wheel --break-system-packages --ignore-installed && "
        "pip3 install aider-chat --break-system-packages --ignore-installed"
    ),
    "n8n": (
        "npm install -g n8n"
    ),
    "ollama_setup": (
        "curl -fsSL https://ollama.com/install.sh | sh"
    )
}

def start_ollama_service():
    def run_server():
        os.system("ollama serve")
    threading.Thread(target=run_server, daemon=True).start()

def execute_agent_setup(agent_key):
    if agent_key not in AGENT_REGISTRY:
        return "❌ [Error]: Unknown Setup Request."
        
    cmd = AGENT_REGISTRY[agent_key]
    # কাজের শুরুতে স্ক্রিনে ইন্ডিকেটর টেক্সট পুশ করা
    logs = f"⏳ [SYSTEM INDICATOR]: 100% Active. Background processing started...\n"
    logs += f"⚙️ Deploying {agent_key.upper()} Environment... Please do not close the app.\n\n"
    
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        logs += f"✅ [Success]: {agent_key.upper()} Core Installed and Configured!\n"
        if agent_key == "ollama_setup":
            start_ollama_service()
            logs += "⚙️ [Service]: Ollama background daemon started successfully."
    else:
        if "already exists" in process.stderr.lower() or "address already in use" in process.stderr.lower():
            return logs + "🔧 [Bypass]: Engine components already active and optimized."
        logs += f"❌ [Log]:\n{process.stderr.strip()}"
        
    return logs

def pull_ollama_model(model_name):
    logs = f"⏳ [OLLAMA INDICATOR]: Connecting to server registry...\n"
    logs += f"⚙️ Fetching free model '{model_name}' weights via cloud bridge...\n\n"
    
    process = subprocess.run(f"ollama pull {model_name}", shell=True, capture_output=True, text=True)
    if process.returncode == 0:
        return logs + f"✅ [Success]: Model '{model_name}' is fully active on AutoKaaj OS!"
    else:
        return logs + f"❌ [Failed]: Ensure Ollama service is running.\nDetails: {process.stderr.strip()}"

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    clean_prompt = prompt.replace('Execute bash:', '').strip().lower()
    
    # ওলামা কোর ও মডেল ডাউনলোডের অটো-ডিটেকশন
    if "ollama" in clean_prompt:
        if "install" in clean_prompt or "setup" in clean_prompt:
            final_output = execute_agent_setup("ollama_setup")
        elif "deepseek" in clean_prompt:
            final_output = pull_ollama_model("deepseek-r1:1.5b")
        elif "qwen" in clean_prompt:
            final_output = pull_ollama_model("qwen2.5:1.5b")
        elif "gemma" in clean_prompt:
            final_output = pull_ollama_model("gemma2:2b")
        else:
            process = subprocess.run(prompt.strip(), shell=True, capture_output=True, text=True)
            final_output = f"🤖 [Ollama]:\n{process.stdout.strip()}\n{process.stderr.strip()}"

    # ওয়ান-ক্লিক অন্যান্য এজেন্ট ইনস্টলেশন
    elif "openmanus" in clean_prompt or "manus" in clean_prompt:
        final_output = execute_agent_setup("openmanus")
    elif "openclaw" in clean_prompt or "claw" in clean_prompt:
        final_output = execute_agent_setup("openclaw")
    elif "claude-code" in clean_prompt or "claude code" in clean_prompt:
        final_output = execute_agent_setup("claudecode")
    elif "aider" in clean_prompt or "codex" in clean_prompt:
        final_output = execute_agent_setup("aider")
    elif "n8n" in clean_prompt:
        final_output = execute_agent_setup("n8n")
        
    # কাস্টম ব্যাশ টার্মিনাল কমান্ড
    elif prompt.strip().startswith(('pip', 'npm', 'apt', 'git', 'ls', 'cd', 'python', 'nohup')):
        logs = f"⏳ [SHELL INDICATOR]: Processing bash pipeline...\n\n"
        process = subprocess.run(prompt.strip(), shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            final_output = logs + f"{process.stdout.strip()}\n\n✅ [Success]"
        else:
            final_output = logs + f"{process.stdout.strip()}\n❌ [Error]:\n{process.stderr.strip()}"
            
    # এআই চ্যাট মোড
    else:
        if clean_prompt in ['hi', 'hello', 'helo']:
            final_output = "🤖 হ্যালো চিরঞ্জিৎ দা! AutoKaaj AI OS-এ আপনাকে স্বাগতম। ওলামা কোর ইঞ্জিন, লাইভ ইন্ডিকেটর সিস্টেম এবং ফ্রি লাইটওয়েট মডেলস (DeepSeek, Qwen) ব্যাকএন্ডে সম্পূর্ণ আপগ্রেড করা হয়েছে। কাজ শুরু করতে বাটন প্রেস করুন!"
        else:
            final_output = f"🤖 [AutoKaaj OS]: চ্যাট রিসিভড। যেকোনো প্লাগইন বা মডেল সেটআপ করতে ওয়ান-ক্লিক বাটন ব্যবহার করুন।"

    return jsonify({"result": final_output, "response": final_output, "status": "success"})

if __name__ == '__main__':
    def check_ollama():
        time.sleep(2)
        subprocess.run("ollama serve > /dev/null 2>&1 &", shell=True)
    threading.Thread(target=check_ollama, daemon=True).start()
    
    app.run(host='0.0.0.0', port=5000, threaded=True)
