from fastapi import APIRouter
from pydantic import BaseModel, Field
import requests
import os
from dotenv import load_dotenv

# Initialize Router
router = APIRouter(prefix="/chatbot", tags=["Groq Chatbot API"])

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Make sure this exact URL is used:
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

class ChatInput(BaseModel):
    message: str = Field(..., description="The user's message")
    language: str = Field("English", description="The current language of the app")

@router.post("")
def chat_with_bot(data: ChatInput):
    if not GROQ_API_KEY:
        return {"response": "Error: GROQ_API_KEY not found in environment variables."}

    # Set up the prompt with strict instructions for brief, bulleted answers
    system_prompt = (
        f"You are the AgroGuard AI Assistant helping farmers. "
        f"You MUST keep your answers extremely brief, to the point, and strictly use bullet points for any advice, steps, or data. "
        f"Never use long paragraphs. "
        f"You MUST respond in this language: {data.language}."
    )

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant", # The correct, currently supported Groq model
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": data.message}
        ],
        "temperature": 0.5, # Lowered slightly for more focused and less rambling answers
        "max_tokens": 300   # Lowered to ensure brief responses
    }

    try:
        response = requests.post(GROQ_URL, headers=headers, json=payload)
        res_json = response.json()

        if "error" in res_json:
             raise Exception(res_json["error"]["message"])

        bot_reply = res_json["choices"][0]["message"]["content"]
        return {"response": bot_reply}

    except Exception as e:
        print(f"⚠️ Groq API Error: {e}")
        return {"response": f"Sorry, I am having trouble connecting right now. ({str(e)})"}