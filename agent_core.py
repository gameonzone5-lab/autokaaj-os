from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess

app = Flask(__name__)
CORS(app)

@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute():
    if request.method == 'OPTIONS': return '', 200
    cmd = request.json.get('cmd', '')
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT, text=True)
        return jsonify({"result": out, "status": "success"})
    except subprocess.CalledProcessError as e:
        return jsonify({"result": e.output, "status": "error"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
