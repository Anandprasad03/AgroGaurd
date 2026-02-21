from fastapi import APIRouter
from pydantic import BaseModel, Field
import requests
import os
import json
import re
from dotenv import load_dotenv

RESPONSE_CACHE = {}

load_dotenv()

router = APIRouter(prefix="/crop_planner", tags=["Crop Planner AI"])

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

class AgentInput(BaseModel):
    last_crop: str = Field(..., max_length=50, description="Previous crop harvested")
    soil_type: str = Field(..., max_length=50, description="Type of soil")
    rainfall: str = Field(..., max_length=50, description="Rainfall level")
    season: str = Field(..., max_length=50, description="Current season")
    region: str = Field("Unknown", max_length=100, description="Farming region")
    language: str = Field("English", max_length=20, description="User's preferred language") # ADDED

@router.post("")
def plan_crop(data: AgentInput):
    # Create cache key including language
    cache_key = f"{data.last_crop}-{data.soil_type}-{data.rainfall}-{data.season}-{data.region}-{data.language}"

    if cache_key in RESPONSE_CACHE:
        print("⚡ Serving Crop Plan from Cache (Instant!)")
        return RESPONSE_CACHE[cache_key]
    
    prompt = f"""
    Act as an expert Agronomist.
    Analyze:
    - Previous Crop: {data.last_crop}
    - Soil: {data.soil_type}
    - Rain: {data.rainfall}
    - Season: {data.season}
    - Region: {data.region}
    
    Task: Create a crop rotation plan.
    
    IMPORTANT LANGUAGE INSTRUCTION:
    Translate ALL text values in the JSON (like 'recommended_crops', 'reasoning', and 'rotation_advice') into {data.language}. 
    Do NOT translate the JSON keys (keep them exactly as "soil_score", "recommended_crops", etc.).
    
    RETURN JSON ONLY. No Markdown outside the values. Format:
    {{
        "soil_score": 85,
        "recommended_crops": ["Crop A", "Crop B"],
        "reasoning": "Why these crops fit...",
        "rotation_advice": "Provide a detailed guide using short paragraphs, bullet points, and bold text for readability."
    }}
    """

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()

        if "error" in res_json:
             raise Exception(f"Google API Error: {res_json['error'].get('message', res_json['error'])}")

        if "candidates" not in res_json or not res_json["candidates"]:
             raise Exception("AI Response Blocked or Empty")

        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]

        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_obj = json.loads(clean_text, strict=False)

        RESPONSE_CACHE[cache_key] = result_obj 
        return result_obj

    except Exception as e:
        print(f"⚠️ AI Agent Error: {e}")
        return {
            "soil_score": 60,
            "recommended_crops": ["Legumes (Fallback)", "Cover Crops"],
            "reasoning": "AI Service is temporarily unavailable. Using standard rotation logic.",
            "rotation_advice": f"**System Note:** We encountered a connection error. Generally, rotating with nitrogen-fixing legumes is a safe strategy to recover soil health."
        }