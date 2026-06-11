import subprocess
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    cmd = prompt.replace('Execute bash:', '').strip()
    if not cmd: return Response("Error: No command received.\n", mimetype='text/plain')

    # ==========================================
    # AUTO-HEALING ENGINE (অটোমেটিক প্রবলেম সলভার)
    # ==========================================
    # যদি কাস্টমার কোনো প্যাকেজ ইনস্টল করতে চায়, সিস্টেম নিজে থেকেই ডিপেন্ডেন্সি ফিক্স করবে
    if "pip3 install" in cmd and "setuptools" not in cmd:
        auto_fix = "pip3 install --upgrade pip setuptools wheel --break-system-packages"
        cmd = f"{auto_fix} && {cmd}"

    def generate():
        yield f"⚙️ [AutoKaaj Engine]: Smart Installer Active...\n"
        
        # Popen ব্যবহার করে লাইভ স্ট্রিম করা
        process = subprocess.Popen(
            cmd, shell=True, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            bufsize=1, 
            universal_newlines=True
        )
        for line in process.stdout:
            yield line # ডেটা আসার সাথে সাথে অ্যাপে লাইভ পুশ করা হবে
            
        process.wait()
        if process.returncode == 0:
            yield f"\n✅ [AutoKaaj]: Setup Completed Successfully!\n"
        else:
            yield f"\n❌ [AutoKaaj]: Setup Failed. Please check logs.\n"

    return Response(generate(), mimetype='text/plain')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
