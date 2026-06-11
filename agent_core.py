import subprocess
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    cmd = request.json.get('cmd', '').replace('Execute bash:', '').strip()
    if not cmd: return Response("Error: No command received.\n", mimetype='text/plain')

    def generate():
        yield f"⚙️ [System]: Executing '{cmd}'...\n"
        # Popen ব্যবহার করে লাইভ স্ট্রিম করা
        process = subprocess.Popen(
            cmd, shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            bufsize=1, 
            universal_newlines=True
        )
        for line in process.stdout:
            yield line # ডেটা আসার সাথে সাথে অ্যাপে পুশ করা হবে
            
        process.wait()
        yield f"\n✅ [Task Completed with code {process.returncode}]\n"

    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
