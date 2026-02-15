async function getPrediction() {
    const inputData = {
        city: document.getElementById("cityInput").value,       // e.g., "Bhubaneswar"
        temperature: parseFloat(document.getElementById("tempInput").value),
        humidity: parseFloat(document.getElementById("humInput").value),
        rainfall: parseFloat(document.getElementById("rainInput").value)
    };

    const response = await fetch("http://127.0.0.1:8000/api/spoilage/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(inputData)
    });

    const result = await response.json();
    alert(`Risk Level: ${result.risk_level}\nConfidence: ${result.confidence}%`);
}// predict.js

const API_URL = "http://localhost:8000/predict/spoilage"; // FastAPI backend URL

async function predict() {
    // 1. Get Values from the DOM
    const crop_type = document.getElementById("crop_type").value;
    const temperature = parseFloat(document.getElementById("temp").value);
    const humidity = parseFloat(document.getElementById("humidity").value);
    const storage_type = document.getElementById("storage").value;
    const days_stored = parseInt(document.getElementById("days").value);

    // 2. Basic Validation
    if (!crop_type || isNaN(temperature) || isNaN(humidity) || isNaN(days_stored)) {
        alert("⚠ Please fill all fields with valid data.");
        return;
    }

    // 3. UI: Show Loader, Hide Result Section
    document.getElementById("loader").style.display = "block";
    document.getElementById("result-section").style.display = "none";

    const payload = {
        crop_type: crop_type,
        temperature: temperature,
        humidity: humidity,
        storage_type: storage_type,
        days_stored: days_stored
    };

    try {
        // 4. Call the API
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        // 5. Parse AI result and Update UI
        // We parse the 'result' string which contains the JSON from Gemini
        const resultData = JSON.parse(data.result.replace(/```json|```/g, "").trim());

        document.getElementById("loader").style.display = "none";
        document.getElementById("result-section").style.display = "block";

        // Update Text Content
        document.getElementById("risk-summary").innerText = `Risk Level: ${resultData.risk_level}`;
        document.getElementById("risk-score-text").innerText = `${resultData.spoilage_risk_percent}%`;
        
        document.getElementById("ai-output").innerHTML = `
            <p><strong>Reasoning:</strong> ${resultData.reasoning}</p>
            <p><strong>Recommendations:</strong> ${resultData.recommendations}</p>
        `;

        // 6. Update the Chart
        createChart(resultData.spoilage_risk_percent);

    } catch (error) {
        console.error("Error:", error);
        document.getElementById("loader").style.display = "none";
        alert("❌ Error connecting to AI Agent. Ensure the backend server is running.");
    }
}

// Chart.js helper function
let riskChart;
function createChart(value) {
    const ctx = document.getElementById('riskChart').getContext('2d');
    
    // Destroy previous chart instance if it exists to prevent overlap
    if (riskChart) {
        riskChart.destroy();
    }

    riskChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Risk', 'Safe'],
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: ['#C53030', '#E2E8F0'], // Red and Gray
                borderWidth: 0
            }]
        },
        options: {
            cutout: '70%',
            plugins: {
                legend: { display: false }
            }
        }
    });
}