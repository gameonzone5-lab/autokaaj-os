import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    cmd = prompt.replace('Execute bash:', '').strip()
    
    if not cmd:
        return jsonify({"result": "Error: No command received", "status": "error"})

    # ==========================================
    # AUTO-HEALING ENGINE
    # ==========================================
    # pip install-এর ক্ষেত্রে setuptools এরর এড়াতে অটো-ফিক্স
    if "pip3 install" in cmd and "setuptools" not in cmd:
        auto_fix = "pip3 install --upgrade pip setuptools wheel --break-system-packages"
        cmd = f"{auto_fix} && {cmd}"

    try:
        # কমান্ড রান হবে এবং ব্যাকগ্রাউন্ডে কাজ শেষ হওয়া পর্যন্ত অপেক্ষা করবে
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        output = process.stdout.strip()
        if process.stderr.strip():
            output += "\n[Logs/Warnings]:\n" + process.stderr.strip()
            
        if not output:
            output = f"Task [{cmd}] executed successfully."

        # অ্যাপ ঠিক যে JSON ফরম্যাটে ডেটা চায়, সেভাবেই পাঠানো হচ্ছে
        return jsonify({
            "result": output, 
            "response": output, 
            "status": "success"
        })
    except Exception as e:
        return jsonify({"result": f"Execution Error: {str(e)}", "status": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
