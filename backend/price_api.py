from fastapi import APIRouter
from pydantic import BaseModel, Field
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
    crop: str = Field(..., max_length=50, description="Name of the crop")
    market_level: str = Field(..., max_length=50, description="Local vs Export market")
    location: str = Field(..., max_length=100, description="Origin location")
    product_type: str = Field(..., max_length=50, description="Standard vs Organic")
    month: str = Field(..., max_length=50, description="Month of sale")
    cost_price: float = Field(..., ge=0, description="Cost price to calculate profit, must be >= 0")
    language: str = Field("English", max_length=20, description="User's preferred language") # ADDED

@router.post("")
def predict_market_price(data: PriceInput):
    # Create a unique key for caching that includes language
    cache_key = f"{data.crop}-{data.market_level}-{data.location}-{data.product_type}-{data.month}-{data.cost_price}-{data.language}"
    
    if cache_key in PRICE_CACHE:
        print(f"⚡ Serving Market Data from Cache: {cache_key}")
        return PRICE_CACHE[cache_key]

    prompt = f"""
    Act as an Agricultural Data Simulator. Provide a simulated market analysis for educational purposes.
    
    Data:
    - Crop: {data.crop}
    - Location: {data.location}
    - Market Level: {data.market_level}
    - Type: {data.product_type}
    - Timeframe: {data.month}
    - Farmer's Cost Price: {data.cost_price}
    
    Instructions:
    1. Determine the local currency symbol for {data.location} (e.g., '₹' for India, '$' for US).
    2. Estimate a realistic selling price in that currency.
    3. Estimate all relevant expenditures (Taxes, Tariffs, GST, Transportation, and Handling) based on the Market Level and Type.
    4. Calculate 'predicted_profit' (Selling Price - {data.cost_price} - Total Expenditures).
    5. Provide exactly 10 alternative markets/locations where this could be sold.
    6. Provide 10 realistic prices for those markets.
    7. Provide 10 profit margins for those markets (Market Price - {data.cost_price} - Estimated Expenditures for that route).
    
    IMPORTANT FORMATTING INSTRUCTION:
    The values for 'expenditure_breakdown', 'analysis', and 'logistics_advice' MUST be formatted exclusively as Markdown bullet points. Do NOT write paragraphs.
    
    IMPORTANT LANGUAGE INSTRUCTION:
    Translate ALL text values in the JSON (like 'top_10_names', 'expenditure_breakdown', 'analysis', and 'logistics_advice') into {data.language}. 
    Do NOT translate the JSON keys (keep them exactly as "currency", "predicted_price", etc.).
    
    RETURN ONLY JSON:
    {{
        "currency": "₹",
        "predicted_price": 2500,
        "predicted_profit": 350,
        "top_10_names": ["Market A", "Market B", ...],
        "top_10_prices": [2500, 2450, ...],
        "top_10_profits": [350, 300, ...],
        "expenditure_breakdown": "- GST (5%): 125\\n- Transport: 25... (strictly bullet points)",
        "analysis": "- Price is expected to rise due to...\\n- High demand in... (strictly bullet points)",
        "logistics_advice": "- Use cold storage for...\\n- Route via... (strictly bullet points)"
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
        
        # Clean and parse JSON
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_json = json.loads(clean_text)
        
        # Save to Cache
        PRICE_CACHE[cache_key] = result_json
        return result_json

    except Exception as e:
        print(f"⚠️ Market AI Error: {e}")
        base_cost = data.cost_price if data.cost_price > 0 else 50.0 
        dummy_price = base_cost * 1.5 
        dummy_expenditure = base_cost * 0.15 # 15% estimated expenditure fallback
        dummy_profit = dummy_price - base_cost - dummy_expenditure
        
        return {
            "currency": "$",
            "predicted_price": round(dummy_price, 2),
            "predicted_profit": round(dummy_profit, 2),
            "top_10_names": [f"{data.location} Hub", "North Region", "South Region", "East Region", "West Region", "Central", "Port A", "Port B", "Border 1", "Border 2"],
            "top_10_prices": [dummy_price + 5, dummy_price + 3, dummy_price + 2, dummy_price, dummy_price - 1, dummy_price - 2, dummy_price - 3, dummy_price - 4, dummy_price - 5, dummy_price - 6],
            "top_10_profits": [dummy_profit + 2, dummy_profit + 1, dummy_profit, dummy_profit - 1, dummy_profit - 2, dummy_profit - 3, dummy_profit - 4, dummy_profit - 5, dummy_profit - 6, dummy_profit - 7],
            "expenditure_breakdown": "- Estimated Transport: 10%\n- Estimated Taxes: 5%\n*AI Unreachable, using fallbacks.*",
            "analysis": "- ⚠️ AI Unreachable\n- Using estimated offline baseline based on your cost price.",
            "logistics_advice": "- Cannot generate dynamic routes at this time.\n- Proceed with standard local logistics."
        }