from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import joblib

router = APIRouter(prefix="/price", tags=["Price Forecast"])

# Load Model
model = joblib.load("ml_models/price/price_model.pkl")

class PriceInput(BaseModel):
    Crop: str
    Location: str
    Supply_Tonnes: float
    Transport_Cost_Per_Km: float
    Fuel_Price: float
    Date: str  # Format: YYYY-MM-DD

@router.post("/predict")
def predict_price(data: PriceInput):
    # Convert to DataFrame
    input_data = data.dict()
    df = pd.DataFrame([input_data])
    
    # Process Date (Same logic as training)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.month
    df["Year"] = df["Date"].dt.year
    df = df.drop(columns=["Date"])

    # Predict
    predicted_price = model.predict(df)[0]

    return {
        "predicted_price": round(float(predicted_price), 2),
        "currency": "INR"
    }