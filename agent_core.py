import subprocess
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# ==========================================
# ADVANCED AUTO-HEALING ENGINE
# ==========================================
def execute_with_auto_heal(original_cmd, max_retries=2):
    cmd = original_cmd
    logs = f"🚀 [AutoKaaj Engine]: Executing '{cmd}'...\n"
    
    for attempt in range(max_retries):
        process = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        output = process.stdout.strip()
        error_out = process.stderr.strip()
        
        if process.returncode == 0:
            logs += f"\n{output}\n✅ [Success]: Task completed automatically."
            return logs
        
        # এরর ধরা পড়লে অটো-হিলিং লজিক শুরু:
        logs += f"\n⚠️ [Attempt {attempt+1} Failed]: Analyzing error...\n"
        combined_err = error_out + output
        
        # প্রবলেম ১: Debian Pip Conflict (যেটা আপনার স্ক্রিনশটে হয়েছে)
        if "uninstall-no-record-file" in combined_err or "Cannot uninstall pip" in combined_err:
            logs += "🔧 [Auto-Fix]: Detected system pip conflict. Applying --ignore-installed bypass...\n"
            cmd = f"{cmd} --ignore-installed"
        
        # প্রবলেম ২: Missing Build Tools (setuptools/wheel)
        elif "BackendUnavailable" in combined_err or "setuptools" in combined_err:
            logs += "🔧 [Auto-Fix]: Missing core build tools. Installing safely...\n"
            subprocess.run("pip3 install --upgrade setuptools wheel --break-system-packages", shell=True)
        
        # প্রবলেম ৩: Externally Managed Environment Block
        elif "externally-managed-environment" in combined_err:
            logs += "🔧 [Auto-Fix]: Environment block detected. Overriding system rules...\n"
            if "--break-system-packages" not in cmd:
                cmd = f"{cmd} --break-system-packages"
                
        # প্রবলেম ৪: OpenManus বা কোনো ডিরেক্টরি না পাওয়া
        elif "No such file or directory" in combined_err and "cd" in cmd:
            logs += "🔧 [Auto-Fix]: Missing directory. Trying to clone repository first...\n"
            repo_name = cmd.split("cd ")[1].split(" ")[0] # ডিরেক্টরির নাম বের করা
            # এখানে একটি ডামি ফিক্স দেওয়া হলো, এটি প্রজেক্ট অনুযায়ী কাস্টমাইজ করা যায়
            cmd = f"echo 'Please run git clone first for {repo_name}'"
        
        else:
            logs += f"❌ [Fatal Error]: AI cannot auto-fix this issue. Details:\n{error_out}"
            return logs
            
    logs += "\n❌ [Failed]: Maximum auto-heal attempts reached."
    return logs

@app.route('/api/generate', methods=['POST', 'OPTIONS'])
@app.route('/api/execute', methods=['POST', 'OPTIONS'])
def execute_command():
    if request.method == 'OPTIONS': return '', 200
    
    data = request.json or {}
    prompt = data.get('prompt', data.get('message', data.get('cmd', '')))
    cmd = prompt.replace('Execute bash:', '').strip()
    
    if not cmd:
        return jsonify({"result": "Error: No command received", "status": "error"})
        
    # অটো-হিলিং ইঞ্জিনের মাধ্যমে কমান্ড পাঠানো হচ্ছে
    final_output = execute_with_auto_heal(cmd)
    
    return jsonify({
        "result": final_output, 
        "response": final_output, 
        "status": "success"
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, threaded=True)
