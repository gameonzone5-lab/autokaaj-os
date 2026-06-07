import json

class AgentBridge:
    def __init__(self):
        self.mailbox = {} # এজেন্টের কাজের সারি

    def send_task(self, sender, receiver, task):
        # এক এজেন্ট থেকে অন্য এজেন্টে মেসেজ পাঠানো
        message = {"sender": sender, "task": task}
        if receiver not in self.mailbox:
            self.mailbox[receiver] = []
        self.mailbox[receiver].append(message)
        print(f"Message from {sender} to {receiver} delivered.")
        return True

    def get_tasks(self, agent_name):
        return self.mailbox.get(agent_name, [])

# ব্রিজ ইঞ্জিন চালু করা
bridge = AgentBridge()
