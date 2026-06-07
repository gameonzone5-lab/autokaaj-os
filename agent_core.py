from flask import Flask, request, Response
from flask_cors import CORS
import subprocess
import os

app = Flask(__name__)
CORS(app)

@app.route('/api/execute', methods=['POST'])
def execute():
    cmd = request.json.get('cmd', '')
    
    # লাইভ স্ট্রিমিং ফাংশন
    def generate():
        # পিপি (Pseudo-terminal) মোডে রান করা যাতে লাইভ আউটপুট আসে
        process = subprocess.Popen(
            cmd, shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            bufsize=1, 
            universal_newlines=True
        )
        for line in process.stdout:
            yield line
    
    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, threaded=True)
