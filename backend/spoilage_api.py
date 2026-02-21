from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
import json
import re
from dotenv import load_dotenv

router = APIRouter(prefix="/spoilage", tags=["Spoilage AI Agent"])

SPOILAGE_CACHE = {}

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Using the stable model version
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

class SpoilageInput(BaseModel):
    action_type: str
    crop_type: str
    # Store-specific fields
    temperature: float = 0.0
    humidity: float = 0.0
    storage_type: str = ""
    days_stored: int = 0
    # Sell-specific fields
    current_location: str = ""
    selling_destination: str = ""

@router.post("/predict")
def predict_spoilage(data: SpoilageInput):
    cache_key = f"{data.action_type}-{data.crop_type}-{round(data.temperature, 1)}-{round(data.humidity, 1)}-{data.storage_type}-{data.days_stored}-{data.current_location}-{data.selling_destination}"
    
    if cache_key in SPOILAGE_CACHE:
        print(f"⚡ Serving Spoilage Data from Cache for: {cache_key}")
        return SPOILAGE_CACHE[cache_key]
        
    # 1. Define the Context based on Action Type
    if data.action_type == "Store":
        context_str = f"- Action: STORE\n- Storage Type: {data.storage_type}\n- Storage Temperature: {data.temperature}°C\n- Storage Humidity: {data.humidity}%\n- Estimated Days to Store: {data.days_stored}"
    else:
        context_str = f"- Action: TRANSPORT & SELL\n- Current Location: {data.current_location}\n- Destination: {data.selling_destination}\n- The AI MUST estimate the average transit temperature, humidity, and transit days based on these locations."

    # 2. Define the Prompt
    prompt = f"""
    You are an AI Spoilage, Logistics, and Strategy Predictor.
    Analyze the risk and strategy for:
    - Crop: {data.crop_type}
    {context_str}

    CRITICAL INSTRUCTIONS:
    1. Assess the spoilage and quality loss risk for the chosen action (0-100 score).
    2. CROSS-ADVICE FEATURE: If the action is "Store", evaluate if it will likely rot or lose market value, and strongly advise them to "Sell" instead. Provide this in `cross_advice`. If the action is "Sell", DO NOT provide cross advice (leave `cross_advice` empty).
    3. TOP ROUTES FEATURE: If the action is "Sell", predict the Top 3 specific routes/methods from {data.current_location} to {data.selling_destination}. **For each route, you MUST explicitly state the estimated transit days** and explain why it is profitable/safe. If Action is "Store", return "N/A" for top_routes.
    4. Provide an `average_transit_days` (integer), `estimated_temp` (float), and `estimated_humidity` (float) if selling. Provide 0 for these if storing.
    
    Return a valid JSON object matching this exact structure:
    {{
        "risk_score": 45,
        "risk_level": "Medium",
        "cross_advice": "⚠️ STRATEGIC WARNING: You chose to Store, but due to high humidity, you should SELL immediately to prevent loss... (or leave empty string if action is Sell or choice is good)",
        "analysis": "Detailed markdown analyzing the spoilage risk of their chosen action.",
        "logistics_recommendation": "Markdown advising on packaging, moisture barriers, and handling.",
        "top_routes": "### Top 3 Profitable Routes\\n1. **Route 1 (Estimated 2 Days):**... (Markdown list. Return 'N/A' if action is Store)",
        "average_transit_days": 3,
        "estimated_temp": 28.5,
        "estimated_humidity": 65.0,
        "logistics_data": {{
            "Refrigerated Transit": 95,
            "Standard Transit": 40,
            "Rail/Bulk": 60
        }}
    }}
    """

    # Enforce JSON mode
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        },
        "safetySettings": [
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_ONLY_HIGH"
            }
        ]
    }
    
    try:
        # 3. Call Gemini
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()

        # 4. Check for Valid Response
        if "error" in res_json:
            raise Exception(f"API Error: {res_json['error']['message']}")
            
        if "candidates" not in res_json or not res_json["candidates"]:
            raise Exception("Blocked by Safety Filters or Empty Response")

        # 5. Extract & Parse
        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_json = json.loads(clean_text)
        
        SPOILAGE_CACHE[cache_key] = result_json
        return result_json

    except Exception as e:
        print(f"⚠️ AI FAILURE: {e}")
        
        # 6. ROBUST FALLBACK (Rule-Based)
        score = 10
        level = "Low"
        cross_msg = ""
        
        # Use estimated fallback numbers if it's a Sell action
        eval_temp = data.temperature if data.action_type == "Store" else 30.0
        eval_hum = data.humidity if data.action_type == "Store" else 70.0
        
        if eval_temp > 30 or eval_hum > 85:
            score = 85
            level = "High"
            if data.action_type == "Store":
                cross_msg = "⚠️ **STRATEGIC WARNING:** Conditions are extremely harsh for storing. You should strongly consider **Selling** immediately or utilizing advanced cold-chain transport."
        elif eval_temp > 25 or (data.action_type == "Store" and data.days_stored > 7):
            score = 55
            level = "Medium"

        return {
            "risk_score": score,
            "risk_level": level,
            "cross_advice": cross_msg,
            "analysis": f"### ⚠️ AI Connection Issue\n**Using offline estimation.**\n- **Estimated Risk:** {level} ({score}%)\n- **Advice:** Evaluate local conditions carefully.",
            "logistics_recommendation": "### 🚚 Offline Logistics\n- Ensure temperature control.\n- Avoid moisture accumulation.",
            "top_routes": "1. Main Highway (Fastest - ~2 Days)\n2. Standard Rail (Economical - ~4 Days)\n3. Local Distributors (~1 Day)" if data.action_type == "Sell" else "N/A",
            "average_transit_days": 3 if data.action_type == "Sell" else 0,
            "estimated_temp": 28.0 if data.action_type == "Sell" else 0,
            "estimated_humidity": 65.0 if data.action_type == "Sell" else 0,
            "logistics_data": {
                "Refrigerated Transit": 95,
                "Standard Transit": 20,
                "Rail/Bulk": 40
            }
        }