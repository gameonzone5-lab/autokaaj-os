import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# অ্যাপের টার্মিনাল এবং এজেন্ট উভয়ের জন্য রুট
@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    # OPTIONS রিকোয়েস্ট (Preflight) এর জন্য
    if request.method == 'OPTIONS': 
        return '', 200
    
    # অ্যাপ থেকে ডেটা গ্রহণ
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    
    # Execute bash: লেখা থাকলে সেটি সরিয়ে ফেলা
    cmd = prompt.replace('Execute bash:', '').strip()
    
    if not cmd:
        return jsonify({"result": "Error: No command received", "status": "error"})
        
    try:
        # আসল টার্মিনাল কমান্ড রান করা
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        output = process.stdout.strip()
        if process.stderr.strip():
            output += "\n[Logs]:\n" + process.stderr.strip()
            
        if not output:
            output = f"Task [{cmd}] executed successfully. (No text output)"
            
        # অ্যাপ ঠিক যে ফরম্যাটে ডেটা চায়, সেভাবেই পাঠানো
        return jsonify({
            "result": output, 
            "response": output, 
            "status": "success"
        })
        
    except Exception as e:
        return jsonify({
            "result": f"Execution Error: {str(e)}", 
            "response": str(e), 
            "status": "error"
        })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
