#!/bin/bash

# ১. মাস্টার পাইথন ইঞ্জিন (এটি কমান্ডের আউটপুট সরাসরি অ্যাপে দেবে)
cat << 'PY' > agent_core.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
app = Flask(__name__)
CORS(app)
@app.route('/api/execute', methods=['POST'])
def execute():
    cmd = request.json.get('cmd', '')
    try:
        # লিনাক্স কমান্ড সরাসরি রান করা
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return jsonify({"result": out, "status": "success"})
    except subprocess.CalledProcessError as e:
        return jsonify({"result": e.output, "status": "error"})
if __name__ == '__main__': app.run(host='127.0.0.1', port=5000)
PY

# ২. মাস্টার অ্যাপ ইন্টারফেস
cat << 'HTML' > index.html
<!DOCTYPE html>
<html>
<body style="background:#000; color:#0f0; font-family:monospace; padding:10px;">
<h3>AutoKaaj OS - Pro System</h3>
<div id="output" style="height:300px; overflow-y:auto; border:1px solid #333; padding:10px; font-size:12px;"></div>
<input type="text" id="cmd" style="width:100%; padding:10px; background:#111; color:#0f0; border:1px solid #333;">
<button onclick="run()" style="width:100%; padding:15px; background:#0f0; font-weight:bold; color:#000;">RUN COMMAND</button>
<script>
async function run() {
    const cmd = document.getElementById('cmd').value;
    const out = document.getElementById('output');
    const res = await fetch('http://127.0.0.1:5000/api/execute', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cmd: cmd})
    });
    const data = await res.json();
    out.innerHTML += '<div><b>$ ' + cmd + '</b><br>' + data.result.replace(/\n/g, '<br>') + '</div>';
    out.scrollTop = out.scrollHeight;
}
</script>
</body>
</html>
HTML

# ৩. অটো-পুশ
git add -A
git commit -m "AutoKaaj OS: Pro Build Final"
git push origin main
echo "--- সব সেটআপ হয়েছে, গিট-এ পুশ হয়েছে ---"
