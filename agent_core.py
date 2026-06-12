import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# CORE EXECUTION ENGINE (টার্মিনাল ও ইনস্টলারের জন্য)
# ==========================================
def bulletproof_execution(cmd):
    logs = f"🚀 [AutoKaaj Engine]: Starting Task...\n"
    
    if "pip install" in cmd or "pip3 install" in cmd:
        logs += "🔧 [System Prep]: Checking dependencies...\n"
        subprocess.run("apt update && apt install -y build-essential python python-dev libffi rust clang", shell=True)
        if "--break-system-packages" not in cmd: cmd += " --break-system-packages"
        if "--ignore-installed" not in cmd: cmd += " --ignore-installed"
    
    logs += f"⏳ Executing: {cmd}\n(Heavy installations take time, please wait...)\n\n"
    
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if process.returncode == 0:
        return logs + f"{process.stdout.strip()}\n\n✅ [Success]: Task completed successfully!"
    else:
        return logs + f"{process.stdout.strip()}\n❌ [Error]:\n{process.stderr.strip()}\n\n❌ [Failed]: Task error."

# ==========================================
# SMART ROUTING (এজেন্ট চ্যাট বনাম সিস্টেম কমান্ড)
# ==========================================
@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    
    # ১. ইনস্টলার ট্যাবের কমান্ড হ্যান্ডলিং
    if "Execute bash:" in prompt:
        cmd = prompt.replace('Execute bash:', '').strip()
        final_output = bulletproof_execution(cmd)
        
    # ২. সরাসরি টার্মিনাল কমান্ড হ্যান্ডলিং (pip, npm, git ইত্যাদি)
    elif prompt.strip().startswith(('pip', 'npm', 'apt', 'git', 'ls', 'cd', 'python', 'nohup')):
        final_output = bulletproof_execution(prompt.strip())
        
    # ৩. এআই এজেন্ট চ্যাট হ্যান্ডলিং (নরমাল কথাবার্তা)
    else:
        user_text = prompt.strip().lower()
        if user_text in ['hi', 'hello', 'helo', 'hey']:
            final_output = "🤖 হ্যালো! আমি AutoKaaj AI Agent। আমি লিনাক্স কমান্ড এক্সিকিউট করতে পারি এবং আপনার সাথে কথাও বলতে পারি। বলুন, আজ আপনাকে কীভাবে সাহায্য করতে পারি?"
        else:
            final_output = f"🤖 [Agent]: আপনি বলেছেন '{prompt}'। আমি এখন এআই চ্যাট মোডে আছি। কোনো প্যাকেজ বা টুল ইনস্টল করতে চাইলে সরাসরি টার্মিনাল কমান্ড (যেমন: pip install...) দিন।"

    return jsonify({
        "result": final_output, 
        "response": final_output, 
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
