#!/bin/bash
echo "[*] AutoKaaj OS: System Auto-Correction Started..."
# সব ফাইল ঠিকঠাক তৈরি করে নেওয়া
git add -A
git commit -m "AutoKaaj OS: Automated Self-Healing Build"
git push origin main
echo "[!] Pushed to GitHub. AutoKaaj OS is now deploying."
