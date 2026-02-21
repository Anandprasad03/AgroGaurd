from fastapi import APIRouter
from pydantic import BaseModel, Field
import requests
import os
import json
import re
from dotenv import load_dotenv

router = APIRouter(prefix="/spoilage", tags=["Spoilage AI Agent"])

SPOILAGE_CACHE = {}

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Keeping your requested model version
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

class SpoilageInput(BaseModel):
    action_type: str = Field(..., max_length=20, description="Store or Sell")
    crop_type: str = Field(..., max_length=50, description="Name of the crop")
    language: str = Field("English", max_length=20, description="User's preferred language") # ADDED LANGUAGE FIELD
    # Store-specific fields
    temperature: float = Field(0.0, ge=-50, le=100, description="Temperature in Celsius")
    humidity: float = Field(0.0, ge=0, le=100, description="Humidity percentage")
    storage_type: str = Field("", max_length=50, description="Type of storage")
    days_stored: int = Field(0, ge=0, description="Number of days stored")
    # Sell-specific fields
    current_location: str = Field("", max_length=100, description="Current location")
    selling_destination: str = Field("", max_length=100, description="Target destination")

@router.post("/predict")
def predict_spoilage(data: SpoilageInput):
    cache_key = f"{data.action_type}-{data.crop_type}-{round(data.temperature, 1)}-{round(data.humidity, 1)}-{data.storage_type}-{data.days_stored}-{data.current_location}-{data.selling_destination}-{data.language}"
    
    if cache_key in SPOILAGE_CACHE:
        print(f"⚡ Serving Spoilage Data from Cache")
        return SPOILAGE_CACHE[cache_key]

    if data.action_type == "Store":
        context = f"""
        Action: STORE
        Crop: {data.crop_type}
        Current Temp: {data.temperature}°C
        Current Humidity: {data.humidity}%
        Storage Type: {data.storage_type}
        Days to Store: {data.days_stored}
        """
        requirements = """
        Focus heavily on storage longevity, fungal/bacterial risk, and exact ventilation/cooling needs.
        Output MUST include "risk_score" (0-100), "risk_level" (Low/Medium/High), "cross_advice", "analysis" (Markdown format), "logistics_recommendation" (N/A for Store).
        Set "top_routes" to "N/A", "average_transit_days" to 0, "estimated_temp" to the input temp, and "estimated_humidity" to the input humidity.
        Provide a "logistics_viability" dictionary with transport modes as keys (e.g., "Refrigerated", "Standard") and percentage viability (0-100) as values.
        """
    else: 
        context = f"""
        Action: SELL / TRANSPORT
        Crop: {data.crop_type}
        Origin: {data.current_location}
        Destination: {data.selling_destination}
        """
        requirements = """
        Focus heavily on transit time, road conditions, climate changes during transport, and best vehicle types.
        Output MUST include "risk_score" (0-100), "risk_level" (Low/Medium/High), "cross_advice", "analysis" (Markdown format), "logistics_recommendation" (Markdown format).
        Provide a string for "top_routes" (list format).
        Provide integers/floats for "average_transit_days", "estimated_temp", and "estimated_humidity".
        Provide a "logistics_viability" dictionary with transport modes as keys and percentage viability (0-100) as values.
        """

    prompt = f"""
    Act as a Post-Harvest Loss Prevention Expert and Supply Chain Analyst.
    {context}
    
    {requirements}

    IMPORTANT LANGUAGE INSTRUCTION:
    Translate ALL text values in the JSON (like 'cross_advice', 'analysis', 'logistics_recommendation', and 'top_routes') into {data.language}. 
    Do NOT translate the JSON keys (keep them exactly as "risk_score", "analysis", etc.).
    
    RETURN ONLY JSON:
    {{
        "risk_score": 45,
        "risk_level": "Medium",
        "cross_advice": "Brief advice on alternative action.",
        "analysis": "### Spoilage Risk Analysis\\n...",
        "logistics_recommendation": "### Transport Strategy\\n...",
        "top_routes": "1. Route A\\n2. Route B",
        "average_transit_days": 2,
        "estimated_temp": 25.5,
        "estimated_humidity": 60.0,
        "logistics_viability": {{"Refrigerated": 95, "Standard": 40, "Rail": 60}}
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {"responseMimeType": "application/json"}
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()
        
        print(f"RAW GOOGLE RESPONSE: {res_json}") # Helps debug if API fails
        
        if "error" in res_json:
             raise Exception(f"Google API Error: {res_json['error'].get('message', res_json['error'])}")
        
        if "candidates" not in res_json:
            raise Exception(f"Invalid AI Response. Raw JSON: {res_json}")
            
        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_json = json.loads(clean_text)
        
        SPOILAGE_CACHE[cache_key] = result_json
        return result_json

    except Exception as e:
        print(f"⚠️ Spoilage AI Error: {e}")
        # Fallback logic
        eval_temp = data.temperature if data.action_type == "Store" else 28.0
        eval_hum = data.humidity if data.action_type == "Store" else 65.0
        score, level, cross_msg = 30, "Low", "Conditions seem standard."
        
        if eval_temp > 30 or eval_hum > 85:
            score, level = 85, "High"
            if data.action_type == "Store": cross_msg = "⚠️ Conditions are extremely harsh for storing. Consider Selling immediately."
        elif eval_temp > 25 or (data.action_type == "Store" and data.days_stored > 7):
            score, level = 55, "Medium"

        return {
            "risk_score": score,
            "risk_level": level,
            "cross_advice": cross_msg,
            "analysis": f"### ⚠️ AI Connection Issue\n**Using offline estimation.**\n- **Estimated Risk:** {level} ({score}%)\n- **Advice:** Evaluate local conditions carefully.",
            "logistics_recommendation": "### 🚚 Offline Logistics\n- Ensure temperature control.\n- Avoid moisture accumulation.",
            "top_routes": "1. Main Highway\n2. Standard Rail" if data.action_type == "Sell" else "N/A",
            "average_transit_days": 3 if data.action_type == "Sell" else 0,
            "estimated_temp": 28.0 if data.action_type == "Sell" else 0,
            "estimated_humidity": 65.0 if data.action_type == "Sell" else 0,
            "logistics_viability": {"Refrigerated": 90, "Standard": 30, "Rail": 50}
        }