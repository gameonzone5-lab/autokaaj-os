const express = require('express');
const cors = require('cors');
const axios = require('axios');
const path = require('path');
const { exec } = require('child_process');

const app = express();
const PORT = 3000;

app.use(cors());
app.use(express.json());

// UI ফোল্ডার সার্ভ করা
app.use(express.static(path.join(__dirname, 'ui')));

// Agent API Route
app.post('/api/execute', async (req, res) => {
    const { prompt, preset, model, apiUrl, apiKey } = req.body;

    try {
        let aiResponse = "";

        // Ollama Local Connection (Termux)
        if (preset.includes('Ollama')) {
            const url = apiUrl || 'http://127.0.0.1:11434/api/generate';
            const response = await axios.post(url, {
                model: model || 'llama3',
                prompt: prompt,
                stream: false
            });
            aiResponse = response.data.response;
        } 
        // Gemini or Groq Cloud Connection
        else {
            // ক্লাউড API এর জন্য আসল ফেচ লজিক (এখানে Gemini/Groq এর এন্ডপয়েন্ট হবে)
            const response = await axios.post(apiUrl, {
                contents: [{ parts: [{ text: prompt }] }]
            }, {
                headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' }
            });
            // রেসপন্স পার্সিং (API ভেদে আলাদা হতে পারে)
            aiResponse = response.data?.candidates?.[0]?.content?.parts?.[0]?.text || "Response received";
        }

        res.json({ success: true, reply: aiResponse });

    } catch (error) {
        console.error("API Error:", error.message);
        res.status(500).json({ success: false, reply: `Connection Error: ${error.message}` });
    }
});

app.listen(PORT, () => {
    console.log(`[AutoKaaj OS] Agent Server running real-time on http://localhost:${PORT}`);
});
