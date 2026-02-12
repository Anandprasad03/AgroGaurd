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
}