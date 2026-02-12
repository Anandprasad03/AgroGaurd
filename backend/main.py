# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .spoilage_api import router as spoilage_router
from .price_api import router as price_router
from .logistics_api import router as logistics_router
from .ai_agent_api import router as ai_agent_router

app = FastAPI(title="Agri Decision Intelligence Backend")

# Allow all frontend origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins (good for testing)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all APIs
app.include_router(spoilage_router)
app.include_router(price_router)
app.include_router(logistics_router)
app.include_router(ai_agent_router)

@app.get("/")
def home():
    return {"message": "Backend Running Successfully!"}
