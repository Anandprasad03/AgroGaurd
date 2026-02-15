from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv

router = APIRouter(prefix="/spoilage", tags=["Spoilage AI Agent"])

load_dotenv()

# Gemini Config (Matches ai_agent_api.py style)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-3-flash-preview:generateContent?key=" + GEMINI_API_KEY
)

class SpoilageInput(BaseModel):
    crop_type: str
    temperature: float
    humidity: float
    storage_type: str
    days_stored: int

def extract_gemini_text(res_json):
    try:
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "The AI agent is currently busy. Please try again in a moment."

@router.post("/predict")
def predict_spoilage(data: SpoilageInput):
    # The prompt asks the AI to act as the prediction engine
    prompt = f"""
    You are an AI Spoilage Predictor. Analyze the following storage conditions:
    - Crop: {data.crop_type}
    - Temp: {data.temperature}°C
    - Humidity: {data.humidity}%
    - Storage: {data.storage_type}
    - Duration: {data.days_stored} days

    Based on these factors, provide:
    1. A 'Risk Score' (0 to 100) where 100 is certain spoilage.
    2. A 'Risk Level' (Low, Medium, or High).
    3. Detailed analysis of why this risk exists.
    4. Steps to extend the shelf life.

    Format the VERY FIRST LINE of your response exactly like this:
    SCORE: [number] | LEVEL: [Low/Medium/High]
    Then provide the detailed analysis in Markdown.
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    
    try:
        response = requests.post(GEMINI_URL, json=payload)
        full_text = extract_gemini_text(response.json())
        
        # Parse the first line for the UI widgets
        first_line = full_text.split('\n')[0]
        try:
            # Extracting the SCORE and LEVEL from the formatted first line
            score = int(first_line.split('|')[0].replace('SCORE:', '').strip())
            level = first_line.split('|')[1].replace('LEVEL:', '').strip()
            analysis = "\n".join(full_text.split('\n')[1:])
        except:
            score, level, analysis = 50, "Medium", full_text

    except Exception as e:
        return {"risk_score": 0, "risk_level": "Error", "analysis": str(e)}

    return {
        "risk_score": score,
        "risk_level": level,
        "analysis": analysis
    }