// crop_agent.js

const API_URL = "http://localhost:8000/agent/plan";  // FastAPI backend URL

async function generateCropPlan() {
    const lastCrop = document.getElementById("last_crop").value;
    const soilType = document.getElementById("soil_type").value;
    const rainfall = document.getElementById("rainfall").value;
    const season = document.getElementById("season").value;

    const outputBox = document.getElementById("agent_output");

    // Basic validation
    if (!lastCrop || !soilType || !rainfall || !season) {
        outputBox.innerHTML = "<span style='color:red;'>⚠ Please fill all fields.</span>";
        return;
    }

    // Loading state
    outputBox.innerHTML = "<em>⏳ Generating crop plan...</em>";

    const payload = {
        last_crop: lastCrop,
        soil_type: soilType,
        rainfall: rainfall,
        season: season
    };

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        // Show AI agent response
        if (data.analysis) {
            outputBox.innerHTML = `
                <h3>🌾 AI Crop Planning Recommendation</h3>
                <p>${data.analysis.replace(/\n/g, "<br>")}</p>
            `;
        } else {
            outputBox.innerHTML = "<span style='color:red;'>AI Error: No analysis returned.</span>";
        }

    } catch (error) {
        console.error(error);
        outputBox.innerHTML = "<span style='color:red;'>❌ Network error. Check server.</span>";
    }
}
