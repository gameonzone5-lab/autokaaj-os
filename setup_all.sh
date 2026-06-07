#!/bin/bash
# অটোনোমাস লিনাক্স সিস্টেম সেটআপ
pkg update -y
pkg install -y git python3 nodejs clang make build-essential
pip3 install --upgrade pip
pip3 install flask flask-cors
# এআই টুলস
npm install -g @anthropic-ai/claude-code n8n
pip3 install aider-chat
