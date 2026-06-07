from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import subprocess

app = Flask(__name__)
CORS(app)

# এই ফাংশনটি টার্মাক্সের মতো এনভায়রনমেন্ট সেট করবে
def run_linux_cmd(cmd):
    # লিনাক্স সিস্টেম পাথ সেট করা
    env = os.environ.copy()
    env['PATH'] = '/data/data/com.termux/files/usr/bin:/bin:/usr/bin'
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, env=env)
    output, _ = process.communicate()
    return output.decode('utf-8')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    cmd = data.get('prompt', '').replace("Execute bash:", "").strip()
    return jsonify({"response": run_linux_cmd(cmd)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
