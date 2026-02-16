from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
import json
import re
from dotenv import load_dotenv
import hashlib 

# 1. Create a simple global dictionary acting as memory
RESPONSE_CACHE = {}

load_dotenv()

router = APIRouter(prefix="/crop_planner", tags=["Crop Planner AI"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

class AgentInput(BaseModel):
    last_crop: str
    soil_type: str
    rainfall: str
    season: str
    region: str = "Unknown"

@router.post("")
def plan_crop(data: AgentInput):
    # Create cache key
    cache_key = f"{data.last_crop}-{data.soil_type}-{data.rainfall}-{data.season}"

    # Serve from cache if exists
    if cache_key in RESPONSE_CACHE:
        print("⚡ Serving from Cache (Instant!)")
        return RESPONSE_CACHE[cache_key]
    
    # 1. Construct Prompt
    prompt = f"""
    Act as an expert Agronomist.
    Analyze:
    - Previous Crop: {data.last_crop}
    - Soil: {data.soil_type}
    - Rain: {data.rainfall}
    - Season: {data.season}
    
    Task: Create a crop rotation plan.
    RETURN JSON ONLY. No Markdown. Format:
    {{
        "soil_score": 85,
        "recommended_crops": ["Crop A", "Crop B"],
        "reasoning": "Why these crops fit...",
        "rotation_advice": "Detailed guide..."
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        # 2. Call Gemini API
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()

        # 3. Check for Safety Blocks / Empty Responses
        if "candidates" not in res_json or not res_json["candidates"]:
             raise Exception("AI Response Blocked or Empty")

        # 4. Extract Text
        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]

        # 5. Clean & Parse JSON (The Critical Fix)
        # Remove ```json and ``` to prevent parsing errors
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_obj = json.loads(clean_text)

        RESPONSE_CACHE[cache_key] = result_obj 
        return result_obj

    except Exception as e:
        print(f"AI Agent Error: {e}")
        # 6. Fallback Response (Prevents "Unexpected Token" error in frontend)
        return {
            "soil_score": 60,
            "recommended_crops": ["Legumes (Fallback)", "Cover Crops"],
            "reasoning": "AI Service is temporarily unavailable. Using standard rotation logic.",
            "rotation_advice": f"**System Note:** We encountered a connection error ({str(e)}). Generally, rotating with nitrogen-fixing legumes is safe."
        }