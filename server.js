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

const SYSTEM_PROMPT = `You are AutoKaaj OS, an autonomous agent.
Always provide output in this format:
[THINKING] ...
[ACTION] <command>
[FINAL_ANSWER] ...

When creating files, use explicit paths. If one command fails, try breaking it down.`;

async function callLLM(history, model, apiUrl, apiKey) {
    const res = await axios.post(apiUrl, { model: model, prompt: history.map(h => `${h.role}: ${h.content}`).join("\n\n"), stream: false });
    return res.data.response;
}

app.post('/api/execute', upload.single('file'), async (req, res) => {
    const { prompt, model, apiUrl, apiKey } = req.body;
    
    let conversationHistory = [{ role: "system", content: SYSTEM_PROMPT }, { role: "user", content: prompt }];
    let uiOutputLog = "";
    
    try {
        let aiResponse = await callLLM(conversationHistory, model, apiUrl, apiKey);
        uiOutputLog += `<span style="color:#A020F0;">${aiResponse}</span><br>`;

        if (aiResponse.includes("[ACTION]")) {
            let cmdMatch = aiResponse.match(/\[ACTION\]\s*(.*)/);
            if (cmdMatch) {
                let cmd = cmdMatch[1].trim().replace(/`/g, '');
                uiOutputLog += `<br><span style="color:#FFD700;"><b>> EXECUTING:</b> ${cmd}</span><br>`;
                
                try {
                    // Force using sh for better redirection handling
                    const { stdout, stderr } = await execPromise(cmd, { shell: '/bin/sh' });
                    let observation = stdout || stderr || "Success (No output)";
                    uiOutputLog += `<span style="color:#39FF14;">> RESULT:</span> ${observation}<br>`;
                } catch (err) {
                    uiOutputLog += `<span style="color:red;">> FAILED:</span> ${err.message}<br>`;
                }
            }
        }
        res.json({ success: true, reply: uiOutputLog });
    } catch (error) {
        res.status(500).json({ success: false, reply: "Backend Error: " + error.message });
    }
});

app.listen(3000, '0.0.0.0', () => console.log('AutoKaaj Core Online on 0.0.0.0:3000'));
