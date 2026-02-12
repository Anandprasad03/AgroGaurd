from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import joblib

router = APIRouter(prefix="/spoilage", tags=["Spoilage Model"])

# Load Pipeline
model = joblib.load("ml_models/spoilage/model.pkl")

class SpoilageInput(BaseModel):
    city: str
    temperature: float
    humidity: float
    rainfall: float

@router.post("/predict")
def predict_spoilage(data: SpoilageInput):
    # Create DataFrame matching training format
    df = pd.DataFrame([{
        "city": data.city,
        "temperature": data.temperature,
        "humidity": data.humidity,
        "rainfall": data.rainfall
    }])
    
    # Predict
    prediction = model.predict(df)[0]
    probs = model.predict_proba(df).max()

    return {
        "risk_level": prediction,  # Returns "Low", "Medium", or "High"
        "confidence": round(float(probs) * 100, 2),
        "advice": get_advice(prediction)
    }

def get_advice(risk):
    if risk == "High":
        return "IMMEDIATE ACTION: Cool storage required. Process within 24 hours."
    elif risk == "Medium":
        return "Monitor humidity. Sell within 3 days."
    else:
        return "Safe. Standard storage conditions apply."