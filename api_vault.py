from cryptography.fernet import Fernet
import json

class ApiVault:
    def __init__(self):
        # একটি সিক্রেট কি তৈরি বা লোড করা
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)

    def save_key(self, service_name, api_key):
        encrypted_key = self.cipher.encrypt(api_key.encode())
        # এখানে ডাটাবেস বা ফাইলে সেভ হবে
        with open(f"{service_name}.vault", "wb") as f:
            f.write(encrypted_key)
        return "Key Saved Securely"

    def get_key(self, service_name):
        with open(f"{service_name}.vault", "rb") as f:
            encrypted_data = f.read()
        return self.cipher.decrypt(encrypted_data).decode()

vault = ApiVault()
