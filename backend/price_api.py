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
# Using the stable model version
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-flash-preview:generateContent?key={GEMINI_API_KEY}"

class PriceInput(BaseModel):
    crop: str
    market_level: str
    location: str
    product_type: str
    month: str
    cost_price: float

@router.post("")
def predict_market_price(data: PriceInput):
    # Create a unique key for caching
    cache_key = f"{data.crop}-{data.market_level}-{data.location}-{data.product_type}-{data.month}-{data.cost_price}"
    
    if cache_key in PRICE_CACHE:
        print(f"⚡ Serving Market Data from Cache: {cache_key}")
        return PRICE_CACHE[cache_key]

    # Prompt Engineering with new priorities, Currency, and Profit logic:
    prompt = f"""
    Act as an Agricultural Data Simulator. Provide a simulated market analysis for educational purposes.
    Analyze the market for the following parameters:
    - Crop: {data.crop}
    - Market Level: {data.market_level} (Priority 1)
    - Location: {data.location} (Country name for National/International, State name for Local)
    - Product Type: {data.product_type} (Priority 2)
    - Harvest Month: {data.month}
    - Farmer's Base Cost Price: {data.cost_price}

    Your prediction MUST prioritize:
    1. The specified Market Level & Location context.
    2. The Product Type (e.g., Organic fetching a premium vs Inorganic).
    3. Regional Demand across various areas (Priority 3).

    CRITICAL INSTRUCTIONS: 
    1. If the Market Level is "National" or "International", explicitly include estimated tariffs, import/export taxes, and export expenditures in your markdown analysis.
    2. Based on the Market Level and Location, determine the correct currency symbol (e.g., "$" or "USD" for International/USA, "₹" for India, "€" for France, "£" for UK). If International, default to USD "$".
    3. Calculate the NET PROFIT for each market. Net Profit = (Predicted Selling Price) - (Farmer's Base Cost Price) - (Estimated Taxes, Tariffs, and Logistics costs for that specific area). 

    Return a valid JSON object matching this exact structure:
    {{
      "currency": "$",
      "predicted_price": 45.5,
      "predicted_profit": 15.5,
      "top_10_names": ["Market 1", "Market 2", "Market 3", "Market 4", "Market 5", "Market 6", "Market 7", "Market 8", "Market 9", "Market 10"],
      "top_10_prices": [50.0, 48.5, 47.0, 45.0, 44.5, 42.0, 40.0, 39.5, 38.0, 35.0],
      "top_10_profits": [20.0, 18.0, 16.5, 14.0, 13.5, 11.0, 9.0, 8.5, 7.0, 4.0],
      "analysis": "### Market Outlook\\nPrices and profits are driven by demand... (Use rich Markdown with bullet points, bold text, and emojis)"
    }}
    """

    # Enforcing JSON mode in the API request
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
        response = requests.post(GEMINI_URL, json=payload)
        res_json = response.json()

        # Check for standard API errors
        if "error" in res_json:
            raise Exception(f"Google API Error: {res_json['error']['message']}")

        # Check if the response was blocked
        if "candidates" not in res_json or not res_json["candidates"]:
            raise Exception(f"AI Response Blocked/Empty. Full response: {json.dumps(res_json)}")

        # Parse AI Response
        ai_text = res_json["candidates"][0]["content"]["parts"][0]["text"]
        
        # Clean up any residual markdown if the model ignores the mimeType
        clean_text = re.sub(r"```json|```", "", ai_text).strip()
        result_json = json.loads(clean_text)
        
        # Save to Cache
        PRICE_CACHE[cache_key] = result_json
        return result_json

    except Exception as e:
        print(f"⚠️ Market AI Error: {e}")
        # Fallback Data (Prevents UI Crash)
        dummy_price = data.cost_price * 1.5 if data.cost_price else 50.0
        dummy_profit = dummy_price - data.cost_price if data.cost_price else 10.0
        
        return {
            "currency": "$",
            "predicted_price": round(dummy_price, 2),
            "predicted_profit": round(dummy_profit, 2),
            "top_10_names": [f"{data.location} Hub", "North Region", "South Region", "East Region", "West Region", "Central", "Port A", "Port B", "Border 1", "Border 2"],
            "top_10_prices": [dummy_price + 5, dummy_price + 3, dummy_price + 2, dummy_price, dummy_price - 1, dummy_price - 2, dummy_price - 3, dummy_price - 4, dummy_price - 5, dummy_price - 6],
            "top_10_profits": [dummy_profit + 2, dummy_profit + 1, dummy_profit, dummy_profit - 1, dummy_profit - 2, dummy_profit - 3, dummy_profit - 4, dummy_profit - 5, dummy_profit - 6, dummy_profit - 7],
            "analysis": f"### ⚠️ Live AI Connection Issue\nUsing cached/offline market estimation due to API restrictions.\n\n- **Target Location:** {data.location}\n- **Market Level:** {data.market_level}\n\nPlease check your server console for the exact error message."
        }