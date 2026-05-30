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

// এখানে এজেন্টের আইডেন্টিটি এবং উবুন্টুর নিয়ম বলে দেওয়া হয়েছে
const SYSTEM_PROMPT = `You are AutoKaaj OS, an advanced autonomous agent.
IMPORTANT CONTEXT: You are running inside an Ubuntu (proot) environment on Android. You MUST use 'apt' for package management, NOT 'pkg'.
Always provide output in this format:
[THINKING] ...
[ACTION] <command>
[FINAL_ANSWER] ...

If you output an [ACTION], wait for the Observation. If the Observation is an error, analyze it, fix your mistake, and provide a new [ACTION]. If successful, provide the [FINAL_ANSWER].`;

async function callLLM(history, model, apiUrl, apiKey) {
    const res = await axios.post(apiUrl, { model: model, prompt: history.map(h => `${h.role}: ${h.content}`).join("\n\n"), stream: false });
    return res.data.response;
}

app.post('/api/execute', upload.single('file'), async (req, res) => {
    const { prompt, model, apiUrl, apiKey } = req.body;

    let conversationHistory = [{ role: "system", content: SYSTEM_PROMPT }, { role: "user", content: prompt }];
    let uiOutputLog = "";
    
    // Agentic Loop Setup (সর্বোচ্চ ৩ বার নিজে নিজে চেষ্টা করবে)
    let step = 0;
    const MAX_STEPS = 3;
    let isComplete = false;

    try {
        while (step < MAX_STEPS && !isComplete) {
            let aiResponse = await callLLM(conversationHistory, model, apiUrl, apiKey);
            
            let displayResponse = aiResponse.replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>');
            uiOutputLog += `<div style="color:#A020F0; margin-bottom:10px;">${displayResponse}</div>`;

            conversationHistory.push({ role: "assistant", content: aiResponse });

            if (aiResponse.includes("[ACTION]")) {
                let cmdMatch = aiResponse.match(/\[ACTION\]\s*(.*)/);
                if (cmdMatch) {
                    let cmd = cmdMatch[1].trim().replace(/`/g, '');
                    uiOutputLog += `<div style="color:#FFD700; background:#222; padding:5px; border-radius:5px;"><b>> EXECUTING:</b> ${cmd}</div>`;

                    let observation = "";
                    try {
                        const { stdout, stderr } = await execPromise(cmd, { shell: '/bin/sh' });
                        observation = stdout || stderr || "Success (No output)";
                        uiOutputLog += `<div style="color:#39FF14; padding-left:10px;"><b>> RESULT:</b> ${observation.substring(0, 300)}${observation.length > 300 ? '...' : ''}</div><br>`;
                    } catch (err) {
                        observation = `Error: ${err.message}`;
                        uiOutputLog += `<div style="color:red; padding-left:10px;"><b>> FAILED:</b> ${observation.substring(0, 300)}${observation.length > 300 ? '...' : ''}</div><br>`;
                    }
                    
                    // Error বা Success এর রেজাল্ট আবার AI কে পাঠানো (Feedback Loop)
                    conversationHistory.push({ role: "user", content: `Observation: ${observation}\nIf there was an error, figure out why and try a new [ACTION]. If successful, provide a [FINAL_ANSWER].` });
                }
            } else if (aiResponse.includes("[FINAL_ANSWER]")) {
                isComplete = true; // কাজ শেষ হলে লুপ বন্ধ হবে
            } else {
                isComplete = true;
            }
            step++;
        }
        
        if (step >= MAX_STEPS && !isComplete) {
            uiOutputLog += `<br><span style="color:orange;">> Agent reached maximum retry limit and stopped.</span>`;
        }

        res.json({ success: true, reply: uiOutputLog });
    } catch (error) {
        res.status(500).json({ success: false, reply: uiOutputLog + "<br><span style='color:red;'>Backend Error: " + error.message + "</span>" });
    }
});

app.listen(3000, '0.0.0.0', () => console.log('AutoKaaj Core Online on 0.0.0.0:3000'));
