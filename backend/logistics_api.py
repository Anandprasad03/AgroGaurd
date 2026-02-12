# backend/logistics_api.py

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/logistics", tags=["Logistics Optimizer"])

class LogisticsInput(BaseModel):
    spoilage_confidence: float
    spoilage_risk: str
    distance_km: float
    predicted_price: float
    current_price: float

@router.post("/optimize")
def optimize_logistics(data: LogisticsInput):

    # basic rule engine
    urgency_score = 0

    if data.spoilage_risk == "High":
        urgency_score += 50
    elif data.spoilage_risk == "Medium":
        urgency_score += 30
    else:
        urgency_score += 10

    if data.predicted_price < data.current_price:
        urgency_score += 40
    else:
        urgency_score -= 20

    recommended_action = (
        "Transport Immediately" if urgency_score >= 60 else
        "Sell in 2-3 Days" if urgency_score >= 30 else
        "Store Longer"
    )

    return {
        "urgency_score": urgency_score,
        "decision": recommended_action
    }
