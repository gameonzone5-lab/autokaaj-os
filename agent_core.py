from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests
import re
import os

app = Flask(__name__)
CORS(app)  # এটি চিরতরে CORS এরর বন্ধ করে দেবে

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"

def execute_termux_command(command):
    """টার্মাক্সে সরাসরি কমান্ড চালানোর ফাংশন"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        return result.stdout + result.stderr
    except Exception as e:
        return str(e)

@app.route('/api/generate', methods=['POST'])
def proxy_to_agent():
    data = request.json
    user_prompt = data.get("prompt", "")
    model = data.get("model", "gemma4:31b-cloud")
    
    # এজেন্টের সুপারপাওয়ার ইনস্ট্রাকশন
    system_instruction = """You are AutoKaaj OS Autonomous Agent running on Termux. 
    You have REAL system access. If the user asks you to create a file, write a python script, or execute a command, YOU MUST output the exact bash command inside ```bash ... ``` blocks.
    Example:
    ```bash
    mkdir new_folder
    echo "hello" > new_folder/test.txt
    ```
    """
    
    payload = {
        "model": model,
        "prompt": system_instruction + "\n\nUser: " + user_prompt,
        "stream": False
    }
    
    try:
        # ১. Ollama-এর কাছে কমান্ড পাঠানো
        response = requests.post(OLLAMA_URL, json=payload).json()
        llm_reply = response.get("response", "")
        
        # ২. LLM-এর উত্তর থেকে কোড ব্লক খুঁজে বের করে তা নিজে থেকে এক্সিকিউট করা
        bash_blocks = re.findall(r'```bash\n(.*?)\n```', llm_reply, re.DOTALL)
        execution_logs = []
        
        for block in bash_blocks:
            log = execute_termux_command(block)
            execution_logs.append(f"\n[ACTION EXECUTED]:\n{block}\n[RESULT]:\n{log}")
            
        final_output = llm_reply
        if execution_logs:
            final_output += "\n\n" + "\n".join(execution_logs)
            
        # ৩. UI-তে ফলাফল পাঠানো
        return jsonify({"response": final_output})
        
    except Exception as e:
        return jsonify({"response": f"System Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
