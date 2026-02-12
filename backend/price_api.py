# backend/price_api.py

from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd
import joblib

router = APIRouter(prefix="/price", tags=["Price Forecast"])

# Load ML model + metadata
model = joblib.load("ml_models/price/price_model.pkl")
features = joblib.load("ml_models/price/price_scaler.pkl")

class PriceInput(BaseModel):
    date: str
    crop: str
    mandi: str

@router.post("/predict")
def predict_price(data: PriceInput):

    df = pd.DataFrame([{
        "date": pd.to_datetime(data.date),
        "crop": data.crop,
        "mandi": data.mandi
    }])

    # Feature Engineering
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["day_of_year"] = df["date"].dt.dayofyear
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df = df.drop(columns=["date"])

    df = pd.get_dummies(df)

    # Add missing columns
    for col in features:
        if col not in df.columns:
            df[col] = 0

    df = df[features]

    price = model.predict(df)[0]

    return {
        "predicted_price": float(price),
        "currency": "INR"
    }
