from fastapi import APIRouter
from pydantic import BaseModel
import requests
import os
import json
import re
from dotenv import load_dotenv

# Initialize Router
router = APIRouter(prefix="/price", tags=["Market Price AI"])

# Simple Cache to save API calls
PRICE_CACHE = {}

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

class PriceInput(BaseModel):
    crop: str
    region: str
    current_price: float
    month: str

@router.post("")
def predict_market_price(data: PriceInput):
    # Create a unique key for caching
    cache_key = f"{data.crop}-{data.region}-{data.month}"
    
    if cache_key in PRICE_CACHE:
        print(f"⚡ Serving Market Data from Cache: {cache_key}")
        return PRICE_CACHE[cache_key]

    # Prompt Engineering for Financial Data
    prompt = f"""
    Act as an Agricultural Economist in India.
    Analyze the market for:
    - Crop: {data.crop}
    - Region: {data.region}
    - Current Season/Month: {data.month}
    - Current Market Price: {data.current_price} INR

    Provide a JSON response with:
    1. "predicted_price": A specific number (float) for next month's expected price.
    2. "trend_months": A list of the next 5 months (strings, e.g. ["Nov", "Dec", "Jan"]).
    3. "trend_prices": A list of 5 predicted prices (floats) corresponding to those months.
    4. "analysis": A detailed markdown analysis covering with bullet points, emojis, and bold text. Avoid long single blocks of text.:
       - Factors affecting price (rain, supply, demand).
       - Profit/Loss sentiment (Should the farmer sell now or store?).
       - Global market influence if applicable.
    
    Return ONLY JSON. No markdown code blocks.
    Example Format:
    {{
      "predicted_price": 25.5,
      "trend_months": ["Oct", "Nov", "Dec", "Jan", "Feb"],
      "trend_prices": [25.5, 28.0, 30.0, 22.0, 20.0],
      "analysis": "### Market Outlook\\nPrices are rising due to..."
    }}
    """

    payload = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()

        if "candidates" not in res_json or not res_json["candidates"]:
            raise Exception("AI Response Blocked/Empty")

        # Parse AI Response
        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_json = json.loads(clean_text)
        
        # Save to Cache
        PRICE_CACHE[cache_key] = result_json
        return result_json

    except Exception as e:
        print(f"⚠️ Market AI Error: {e}")
        # Fallback Data (Prevents UI Crash)
        return {
            "predicted_price": data.current_price,
            "trend_months": ["Month 1", "Month 2", "Month 3", "Month 4", "Month 5"],
            "trend_prices": [data.current_price] * 5,
            "analysis": "### ⚠️ Service Unavailable\nCould not fetch real-time market data. Please try again later."
        }