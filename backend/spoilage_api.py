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
    crop_type: str
    temperature: float
    humidity: float
    storage_type: str
    days_stored: int

@router.post("/predict")
def predict_spoilage(data: SpoilageInput):
    cache_key = f"{data.crop_type}-{round(data.temperature, 1)}-{round(data.humidity, 1)}-{data.storage_type}-{data.days_stored}"
    if cache_key in SPOILAGE_CACHE:
        print(f"⚡ Serving Spoilage Data from Cache for: {cache_key}")
        return SPOILAGE_CACHE[cache_key]
        
    # 1. Define the Prompt (Updated to include logistics logic and data structure)
    prompt = f"""
    You are an AI Spoilage & Logistics Predictor.
    Analyze:
    - Crop: {data.crop_type}
    - Temp: {data.temperature}°C, Humidity: {data.humidity}%
    - Storage: {data.storage_type}, Days: {data.days_stored}

    Return strict JSON ONLY. No markdown wrappers. Format:
    {{
        "risk_score": 0-100,
        "risk_level": "Low/Medium/High",
        "analysis": "Use rich Markdown: short paragraphs, bullet points, emojis, and bold text regarding spoilage.",
        "logistics_recommendation": "Use rich Markdown: Suggest best transport modes, packaging advice, and routing strategies.",
        "logistics_data": {{
            "Refrigerated Truck": 0-100,
            "Standard Truck": 0-100,
            "Rail Freight": 0-100
        }}
    }}
    Note: logistics_data should represent the viability/safety score (0-100) of each transport mode given the current crop's condition.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        # 2. Call Gemini
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()

        # 3. Check for Valid Response
        if "error" in res_json:
            raise Exception(f"API Error: {res_json['error']['message']}")
            
        if "candidates" not in res_json or not res_json["candidates"]:
            raise Exception("Blocked by Safety Filters or Empty Response")

        # 4. Extract & Parse
        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_json = json.loads(clean_text)
        
        SPOILAGE_CACHE[cache_key] = result_json
        return result_json

    except Exception as e:
        print(f"⚠️ AI FAILURE: {e}")
        
        # 5. ROBUST FALLBACK (Rule-Based)
        # Upgraded fallback to accommodate the new logistics expectations without breaking the UI.
        score = 10
        level = "Low"
        
        if data.temperature > 30 or data.humidity > 85:
            score = 85
            level = "High"
        elif data.temperature > 25 or data.days_stored > 7:
            score = 55
            level = "Medium"

        return {
            "risk_score": score,
            "risk_level": level,
            "analysis": f"""
            ### ⚠️ AI Connection Issue
            **Using offline estimation.**
            
            - **Estimated Risk:** {level} ({score}%)
            - **Reason:** Temperature/humidity thresholds evaluated.
            - **Advice:** Inspect crops immediately. Ensure ventilation.
            
            *(Technical Error: {str(e)})*
            """,
            "logistics_recommendation": """
            ### 🚚 Offline Logistics Routing
            - **Immediate Action:** Utilize temperature-controlled transit.
            - **Packaging:** Ensure moisture barriers are intact.
            - **Transit Route:** Opt for the shortest viable path to market to prevent further degradation.
            """,
            "logistics_data": {
                "Refrigerated Truck": 95,
                "Standard Truck": 20,
                "Rail Freight": 40
            }
        }