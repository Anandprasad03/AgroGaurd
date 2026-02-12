# backend/ai_agent_api.py

from fastapi import APIRouter
from pydantic import BaseModel
import requests
import json

router = APIRouter(prefix="/agent", tags=["Crop Planning AI Agent"])

# ---------------------------
# GEMINI API CONFIG
# ---------------------------
GEMINI_API_KEY = "gen-lang-client-0813549634"
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY
)

# ---------------------------
# INPUT SCHEMA
# ---------------------------

class AgentInput(BaseModel):
    last_crop: str
    soil_type: str
    rainfall: str
    season: str  


# ---------------------------
# ROUTE: Crop Planner AI Agent
# ---------------------------

@router.post("/plan")
def crop_plan(data: AgentInput):

    prompt = f"""
    You are an agricultural expert AI system. Based on:
    - Last crop: {data.last_crop}
    - Soil type: {data.soil_type}
    - Rainfall: {data.rainfall}
    - Growing season: {data.season}

    Provide a detailed agricultural report including:

    1. Best next crop to grow (scientifically justified)
    2. Soil regeneration and nutrient recovery advice
    3. Crop rotation cycle (with reasoning)
    4. Risk factors (weather, pests, soil, economics)
    5. Additional actionable suggestions for farmers
    """

    payload = {
        "contents": [
            {"parts": [{"text": prompt}]}
        ]
    }

    try:
        response = requests.post(GEMINI_URL, json=payload)
        response_json = response.json()

        answer = response_json["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        answer = f"Gemini Agent Error: {str(e)}"

    return {"analysis": answer}
