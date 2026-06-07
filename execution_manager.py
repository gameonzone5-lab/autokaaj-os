import subprocess
import threading
import time
from queue import Queue

class TaskManager:
    def __init__(self):
        self.active_tasks = {}

    def run_task(self, task_name, command):
        task_id = str(int(time.time()))
        self.active_tasks[task_id] = {"name": task_name, "status": "running"}
        # ব্যাকগ্রাউন্ডে টাস্ক চালানো
        threading.Thread(target=self._execute, args=(task_id, command)).start()
        return task_id

    def _execute(self, task_id, command):
        try:
            process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            while True:
                line = process.stdout.readline()
                if not line: break
            self.active_tasks[task_id]["status"] = "completed"
        except:
            self.active_tasks[task_id]["status"] = "failed"

manager = TaskManager()
