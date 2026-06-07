from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import requests

app = Flask(__name__)
# এটি ব্রাউজারের "Failed to fetch" বা "CORS" ব্লক সমস্যার সমাধান করবে
CORS(app) 

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    
    # যদি এটি টার্মিনাল কমান্ড বা Installer Hub-এর টাস্ক হয়
    if prompt.startswith("Execute bash:"):
        cmd = prompt.replace("Execute bash:", "").strip().replace("`", "")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            out = result.stdout if result.stdout else result.stderr
            return jsonify({"response": f"[TERMINAL OUTPUT]:\n{out}\n\n✅ Task Completed!"})
        except Exception as e:
            return jsonify({"response": f"[ERROR]: {str(e)}"})

    # যদি এটি সাধারণ এআই টাস্ক হয় (Ollama-কে পাঠাবে)
    try:
        model = data.get('model', 'gemma4:31b-cloud')
        response = requests.post("http://127.0.0.1:11434/api/generate", 
                                 json={"model": model, "prompt": prompt, "stream": False})
        res_data = response.json()
        return jsonify({"response": res_data.get('response', 'Success')})
    except Exception as e:
        return jsonify({"response": f"[OLLAMA ERROR]: Ensure Ollama is running in background. Error: {str(e)}"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
