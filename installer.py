import subprocess
from execution_manager import manager

class ToolInstaller:
    def install_tool(self, tool_name):
        # প্রতিটি টুলের জন্য আলাদা কমান্ড
        commands = {
            "claude": "npm install -g @anthropic-ai/claude-code",
            "ollama": "curl -fsSL https://ollama.com/install.sh | sh",
            "openmanus": "git clone https://github.com/mannaandpoem/OpenManus.git"
        }
        cmd = commands.get(tool_name.lower())
        if cmd:
            return manager.run_task(f"Installing {tool_name}", cmd)
        return "Tool not found"

installer = ToolInstaller()
