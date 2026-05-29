const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');
const multer = require('multer');
const fs = require('fs');
const { spawn, exec } = require('child_process');
const util = require('util');
const execPromise = util.promisify(exec);

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'ui')));
const upload = multer({ dest: 'uploads/' });

// Auto-start Ollama in background
const ollamaProcess = spawn('ollama', ['serve'], { detached: true, stdio: 'ignore' });
ollamaProcess.unref();

// Autonomous Agent System Prompt
const SYSTEM_PROMPT = `You are AutoKaaj OS, an advanced Autonomous AI Agent running in a Termux (Linux/Android) environment.
You can execute terminal commands to build apps, edit videos, manage files, or solve problems.

Follow this EXACT format for EVERY response:
[THINKING] Explain your thought process and what you plan to do next.
[ACTION] <write only the terminal command here, nothing else>

If you have completed the user's task or just need to talk to the user, use:
[THINKING] I have finished the task.
[FINAL_ANSWER] <your final message to the user>`;

// Helper function to call APIs (Ollama, Gemini, OpenAI, etc.)
async function callLLM(history, preset, model, apiUrl, apiKey) {
    if (apiUrl.includes('11434')) {
        // Local Ollama
        let promptText = history.map(h => `${h.role}: ${h.content}`).join("\n\n");
        const res = await axios.post(apiUrl, { model: model, prompt: promptText, stream: false });
        return res.data.response;
    } else if (apiUrl.includes('generativelanguage')) {
        // Google Gemini
        let promptText = history.map(h => `${h.role}: ${h.content}`).join("\n\n");
        const res = await axios.post(`${apiUrl}?key=${apiKey}`, { contents: [{ parts: [{ text: promptText }] }] }, { headers: { 'Content-Type': 'application/json' } });
        return res.data?.candidates?.[0]?.content?.parts?.[0]?.text || "Gemini Error";
    } else {
        // Universal (OpenAI/Groq format)
        const res = await axios.post(apiUrl, { model: model, messages: history }, { headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' } });
        return res.data?.choices?.[0]?.message?.content || JSON.stringify(res.data);
    }
}

app.post('/api/execute', upload.single('file'), async (req, res) => {
    const { prompt, preset, model, apiUrl, apiKey } = req.body;
    const file = req.file; 
    
    try {
        let fileStatus = file ? `\n[System Note: User uploaded a file to ${file.path}]` : "";
        let finalPrompt = prompt + fileStatus;
        
        let conversationHistory = [
            { role: "system", content: SYSTEM_PROMPT },
            { role: "user", content: finalPrompt }
        ];

        let uiOutputLog = ""; // This will show real-time thinking on UI
        let loopCount = 0;
        const MAX_STEPS = 5; // To prevent infinite loops

        // The Autonomous Agentic Loop
        while (loopCount < MAX_STEPS) {
            loopCount++;
            
            // 1. Get Agent's Thought/Action
            let aiResponse = await callLLM(conversationHistory, preset, model, apiUrl, apiKey);
            conversationHistory.push({ role: "assistant", content: aiResponse });
            
            // Display Agent's raw output on UI
            uiOutputLog += `<span style="color:#A020F0;">${aiResponse}</span>\n\n`;

            // 2. Check if Agent has a Final Answer
            if (aiResponse.includes("[FINAL_ANSWER]")) {
                let finalAns = aiResponse.split("[FINAL_ANSWER]")[1] || "Task Completed.";
                uiOutputLog += `<span style="color:#00FFCC; font-weight:bold;">> FINAL OUTPUT:</span>\n${finalAns.trim()}`;
                break;
            } 
            
            // 3. Execute Terminal Command if Agent wants to take ACTION
            else if (aiResponse.includes("[ACTION]")) {
                let cmdMatch = aiResponse.match(/\[ACTION\]([\s\S]*?)(?=\[THINKING\]|\[FINAL_ANSWER\]|$)/);
                if (cmdMatch && cmdMatch[1]) {
                    let cmd = cmdMatch[1].trim();
                    uiOutputLog += `<span style="color:#FFD700; font-weight:bold;">> SYSTEM EXECUTING:</span> ${cmd}\n`;
                    
                    try {
                        const { stdout, stderr } = await execPromise(cmd);
                        let observation = stdout || stderr || "Command executed successfully with no output.";
                        uiOutputLog += `<span style="color:#39FF14;">> OBSERVATION:</span>\n${observation}\n\n`;
                        
                        // Send observation back to Agent so it knows what happened
                        conversationHistory.push({ role: "user", content: `[OBSERVATION]\n${observation}\nNow continue.` });
                    } catch (err) {
                        uiOutputLog += `<span style="color:red;">> SYSTEM ERROR:</span>\n${err.message}\n\n`;
                        conversationHistory.push({ role: "user", content: `[ERROR]\n${err.message}\nFix the error and try again.` });
                    }
                }
            } else {
                // Failsafe if Agent breaks format
                break;
            }
        }

        if (file) fs.unlinkSync(file.path); 
        res.json({ success: true, reply: uiOutputLog });

    } catch (error) {
        if (file && fs.existsSync(file.path)) fs.unlinkSync(file.path);
        res.status(500).json({ success: false, reply: `> SYSTEM CRASH: ${error.message}` });
    }
});

app.listen(3000, () => console.log('AutoKaaj Autonomous Core Online on port 3000'));
