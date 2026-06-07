#!/bin/bash

# ১. মাস্টার পাইথন ইঞ্জিন (আউটপুটসহ)
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
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return jsonify({"result": out, "status": "success"})
    except subprocess.CalledProcessError as e:
        return jsonify({"result": e.output, "status": "error"})
if __name__ == '__main__': app.run(host='127.0.0.1', port=5000)
PY

# ২. মাস্টার ইউআই (আউটপুটসহ)
cat << 'HTML' > index.html
<!DOCTYPE html>
<html>
<body style="background:#000; color:#0f0; font-family:monospace; padding:10px;">
<div id="terminal-out" style="height:300px; overflow-y:auto; border:1px solid #333;"></div>
<input type="text" id="cmd-input" style="width:100%; background:#111; color:#0f0; padding:10px;">
<button onclick="run()" style="width:100%; padding:15px; background:#0f0; color:#000;">EXECUTE</button>
<script>
async function run() {
    const cmd = document.getElementById('cmd-input').value;
    const out = document.getElementById('terminal-out');
    const res = await fetch('http://127.0.0.1:5000/api/execute', {
        method: 'POST', headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({cmd: cmd})
    });
    const data = await res.json();
    out.innerHTML += '<div>root@autokaaj:~# ' + cmd + '<br>' + data.result.replace(/\n/g, '<br>') + '</div>';
}
</script>
</body>
</html>
HTML

# ৩. গিট অটো-পুশ
git add -A
git commit -m "AutoKaaj OS: Final Unified Build"
git push origin main
echo "--- সব সেটআপ হয়েছে এবং গিট-এ পুশ করা হয়েছে ---"
