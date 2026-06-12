import subprocess
import os
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# MASTER AGENT COMMAND REGISTRY (প্রি-সেটআপ স্ক্রিপ্ট)
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
    )
}

def execute_agent_setup(agent_key):
    if agent_key not in AGENT_REGISTRY:
        return "❌ [Error]: Requesting an unregistered or unknown Agent Setup."
        
    cmd = AGENT_REGISTRY[agent_key]
    logs = f"🚀 [AutoKaaj Brain]: Auto-Configuring & Deploying '{agent_key.upper()}' Engine...\n"
    logs += f"⏳ Running system script packages. Please wait...\n\n"
    
    # ব্যাকগ্রাউন্ডে সাবপ্রসেস এক্সিকিউশন
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        logs += f"{process.stdout.strip()}\n\n✅ [Success]: {agent_key.upper()} Integration Complete and Ready to Use!"
    else:
        # হ্যান্ডশেক বা কোনো ডিরেক্টরি বাগ থাকলে সেকেন্ডারি স্মার্ট ফিক্সিং
        if "already exists" in process.stderr.lower():
            logs += f"🔧 [Directory Detected]: Shifting to Force-Update and Build Routine...\n"
            fix_cmd = f"cd {agent_key.capitalize()} || cd {agent_key.upper()} && git pull && pip3 install -r requirements.txt --break-system-packages --ignore-installed"
            retry = subprocess.run(fix_cmd, shell=True, capture_output=True, text=True)
            if retry.returncode == 0:
                return logs + f"\n✅ [Success Override]: Existing framework updated and stabilized!"
        
        logs += f"{process.stdout.strip()}\n❌ [System Breakdown Log]:\n{process.stderr.strip()}"
        
    return logs

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    
    # অ্যাপের ইনপুট ফিল্টারিং এবং অটো-ডিটেকশন লজিক
    clean_prompt = prompt.replace('Execute bash:', '').strip().lower()
    
    # ১. কাস্টমার যদি বাটনে ক্লিক করে বা সরাসরি এজেন্টের নাম লেখে
    if "openmanus" in clean_prompt or "manus" in clean_prompt:
        final_output = execute_agent_setup("openmanus")
    elif "openclaw" in clean_prompt or "claw" in clean_prompt:
        final_output = execute_agent_setup("openclaw")
    elif "claude-code" in clean_prompt or "claude code" in clean_prompt:
        final_output = execute_agent_setup("claudecode")
    elif "aider" in clean_prompt or "codex" in clean_prompt:
        final_output = execute_agent_setup("aider")
    elif "n8n" in clean_prompt:
        final_output = execute_agent_setup("n8n")
        
    # ২. কাস্টমার যদি ম্যানুয়াল কোনো লিনাক্স কমান্ড ব্যবহার করতে চায়
    elif prompt.strip().startswith(('pip', 'npm', 'apt', 'git', 'ls', 'cd', 'python', 'nohup')):
        logs = f"🚀 [AutoKaaj Shell]: Executing Custom Command...\n"
        process = subprocess.run(prompt.strip(), shell=True, capture_output=True, text=True)
        if process.returncode == 0:
            final_output = logs + f"{process.stdout.strip()}\n\n✅ [Success]"
        else:
            final_output = logs + f"{process.stdout.strip()}\n❌ [Error]:\n{process.stderr.strip()}"
            
    # ৩. নরমাল চ্যাটিং বা গ্রিটিংস মোড
    else:
        if clean_prompt in ['hi', 'hello', 'helo']:
            final_output = "🤖 হ্যালো! আমি AutoKaaj AI OS সেন্ট্রাল এজেন্ট। সমস্ত ক্লাউড এনভায়রনমেন্ট এবং ওয়ান-ক্লিক ইনস্টলার ব্যাকএন্ডে রেডি আছে। আপনি যেকোনো বাটনে ক্লিক করে কাজ শুরু করতে পারেন!"
        else:
            final_output = f"🤖 [AutoKaaj OS]: চ্যাট রিসিভড। আপনি যদি কোনো নির্দিষ্ট এজেন্ট প্লাগিন বিল্ড করতে চান, তবে ইনস্টলার অপশনটি বেছে নিন।"

    return jsonify({"result": final_output, "response": final_output, "status": "success"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
