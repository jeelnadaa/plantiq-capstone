const express = require("express");
<<<<<<< HEAD
const multer = require("multer");
const router = express.Router();

const upload = multer({ storage: multer.memoryStorage() });
const RAG_URL = process.env.RAG_URL || "http://localhost:5001";

router.get("/test", (req, res) => {
    res.send("Chatbot route working");
});

router.post("/chat", upload.any(), async (req, res) => {
    const query = (req.body.query || "").trim();
    const hasImage = Array.isArray(req.files) && req.files.length > 0;

    if (!query) {
        if (hasImage) {
            return res.json({
                answer: "I can't analyze images in chat yet — please describe your question in words instead."
            });
        }
        return res.status(400).json({ error: "No query provided" });
    }

    try {
        const ragRes = await fetch(`${RAG_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, provider: "gemini", mode: "fast" }),
        });

        if (!ragRes.ok) {
            throw new Error(`RAG service responded ${ragRes.status}`);
        }

        const results = await ragRes.json();
        const answer = results?.[0]?.answer || "I couldn't find an answer to that.";
        res.json({ answer });
    } catch (err) {
        console.error("RAG proxy error:", err.message);
        res.status(502).json({ error: "AI assistant is currently unavailable. Make sure the RAG service is running." });
    }
});

router.post("/scan", upload.any(), async (req, res) => {
    const latitude = req.body.latitude;
    const longitude = req.body.longitude;
    const question = (req.body.question || "").trim();

    if (!latitude || !longitude) {
        return res.status(400).json({ error: "Location is required." });
    }

    try {
        const weatherUrl =
            `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}` +
            `&current=temperature_2m,relative_humidity_2m,precipitation,rain,wind_speed_10m,cloud_cover,soil_temperature_0cm,soil_moisture_0_to_1cm` +
            `&timezone=auto`;

        const weatherRes = await fetch(weatherUrl);
        if (!weatherRes.ok) {
            throw new Error(`Open-Meteo responded ${weatherRes.status}`);
        }
        const weather = await weatherRes.json();
        const current = weather.current || {};

        const envData = {
            "Temperature (°C)": current.temperature_2m,
            "Humidity (%)": current.relative_humidity_2m,
            "Precipitation (mm)": current.precipitation,
            "Rain (mm)": current.rain,
            "Wind Speed (km/h)": current.wind_speed_10m,
            "Cloud Cover (%)": current.cloud_cover,
            "Soil Temperature (°C)": current.soil_temperature_0cm,
            "Soil Moisture (m³/m³)": current.soil_moisture_0_to_1cm,
        };

        const query = question ||
            "Give a general coffee crop health advisory based on the current environmental conditions at this location.";

        const ragRes = await fetch(`${RAG_URL}/query`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query, provider: "gemini", env_data: envData }),
        });

        if (!ragRes.ok) {
            throw new Error(`RAG service responded ${ragRes.status}`);
        }

        const results = await ragRes.json();
        const answer = results?.[0]?.answer || "I couldn't generate an advisory for this location.";
        res.json({ answer, environment: envData });
    } catch (err) {
        console.error("Scan proxy error:", err.message);
        res.status(502).json({ error: "Advisory service is currently unavailable." });
    }
});

module.exports = router;
=======
const router = express.Router();

router.get("/test", (req,res)=>{
    res.send("Chatbot route working");
});

module.exports = router;
>>>>>>> d6b66db (first commit)
