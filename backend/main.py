# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.ai_agent_api import router as agent_router
from backend.spoilage_api import router as spoilage_router # Check this import
from backend.price_api import router as price_router
from backend.chatbot_api import router as chatbot_router # Check this import

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # This allows your HTML to talk to the API
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(agent_router)
app.include_router(spoilage_router) # Make sure this line exists
app.include_router(price_router) # Make sure this line exists
app.include_router(chatbot_router) # Make sure this line exists