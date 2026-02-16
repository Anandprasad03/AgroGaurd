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
    # 1. Define the Prompt
    prompt = f"""
    You are an AI Spoilage Predictor.
    Analyze:
    - Crop: {data.crop_type}
    - Temp: {data.temperature}°C, Humidity: {data.humidity}%
    - Storage: {data.storage_type}, Days: {data.days_stored}

    Return strict JSON ONLY. No markdown. Format:
    {{
        "risk_score": 0-100,
        "risk_level": "Low/Medium/High",
        "analysis": "Detailed markdown explanation here..."
    }}
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
        # This runs if Gemini fails, ensuring the UI never breaks.
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
            - **Reason:** High temperature/humidity detected.
            - **Advice:** Inspect crops immediately. Ensure ventilation.
            
            *(Technical Error: {str(e)})*
            """
        }