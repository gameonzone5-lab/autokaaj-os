import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

def bulletproof_execution(cmd):
    logs = f"🚀 [AutoKaaj Engine]: Starting Task...\n"
    
    # Pre-emptive Fix: যদি পাইথন ইনস্টলেশনের কমান্ড হয়, তবে টার্মাক্সের কোর টুলস আগে ইনস্টল করে নেওয়া
    if "pip install" in cmd or "pip3 install" in cmd:
        logs += "🔧 [System Prep]: Checking and installing Termux core build tools (C/Rust compilers)...\n"
        # টার্মাক্সের জন্য অত্যন্ত জরুরি ডিপেন্ডেন্সিগুলো ইনস্টল করা
        subprocess.run("apt update && apt install -y build-essential python python-dev libffi rust clang", shell=True)
        
        # ডেবিয়ান এরর ব্লক করার জন্য সেফটি ফ্ল্যাগ
        if "--break-system-packages" not in cmd:
            cmd += " --break-system-packages"
        if "--ignore-installed" not in cmd:
            cmd += " --ignore-installed"
    
    logs += f"⏳ Executing: {cmd}\n(Please wait, heavy installations take time...)\n\n"
    
    # আসল কমান্ড রান করা
    process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = process.stdout.strip()
    error_out = process.stderr.strip()
    
    if process.returncode == 0:
        logs += f"{output}\n\n✅ [Success]: Task completed successfully!"
    else:
        logs += f"{output}\n\n❌ [Error Output]:\n{error_out}\n\n❌ [Failed]: Task encountered a fatal system error."
        
    return logs

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    cmd = prompt.replace('Execute bash:', '').strip()
    
    if not cmd:
        return jsonify({"result": "Error: No command received", "status": "error"})
        
    final_output = bulletproof_execution(cmd)
    
    return jsonify({
        "result": final_output, 
        "response": final_output, 
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
