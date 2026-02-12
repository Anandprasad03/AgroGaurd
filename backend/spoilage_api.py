# backend/spoilage_api.py

from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import joblib

router = APIRouter(prefix="/spoilage", tags=["Spoilage Model"])

# Load model + encoders
model = joblib.load("ml_models/spoilage/model.pkl")
encoders = joblib.load("ml_models/spoilage/encoders.pkl")
target_encoder = joblib.load("ml_models/spoilage/target_encoder.pkl")

class SpoilageInput(BaseModel):
    temperature: float
    humidity: float
    storage_days: int
    crop_type: str
    storage_type: str
    packaging_type: str

@router.post("/predict")
def predict_spoilage(data: SpoilageInput):

    df = pd.DataFrame([data.dict()])

    # Apply label encoders
    for col, encoder in encoders.items():
        df[col] = encoder.transform(df[col])

    pred = model.predict(df)[0]
    prob = model.predict_proba(df).max()

    risk = target_encoder.inverse_transform([pred])[0]

    return {
        "risk": risk,
        "confidence": float(prob)
    }
