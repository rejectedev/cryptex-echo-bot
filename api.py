from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from cryptex_echo import run_echo
from webull_adapter import save_credentials
from graei_chat import process_chat_message
from api_algo import router as algo_router
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(
    title="Cryptex Echo API",
    description="Trading bot API with AI chat capabilities",
    version="1.0.0"
)

# Include algorithm router
app.include_router(router=algo_router, prefix="/algo", tags=["Algorithm Lab"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "Cryptex Echo API is running",
        "endpoints": [
            "/chat - AI Chat Interface",
            "/pearls - Trading Log",
            "/royalties - Royalty Information",
              "/run-trade - Execute Trade",
              "/algo/simulate - Simulate Trading Algorithm",
              "/algo/ai-assist - Get AI Algorithm Assistance"
        ]
    }

# Enable CORS
frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        frontend_url
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)

@app.get("/pearls")
async def get_pearls():
    try:
        with open("pearl_log.txt", "r") as f:
            content = f.read()
        return {"content": content}
    except FileNotFoundError:
        return {"content": "No trades yet."}

@app.get("/royalties")
async def get_royalties():
    try:
        with open("royalty/logs/royalty_log.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

from pydantic import BaseModel

class ChatMessage(BaseModel):
    message: str

@app.post("/chat")
async def chat(message: ChatMessage):
    try:
        if not message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = process_chat_message(message.message)
        # Convert response to ASCII-safe string
        if response is None:
            response = "No response generated"
        
        return {
            "reply": str(response),
            "status": "success",
            "timestamp": datetime.utcnow().isoformat()
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"Error processing chat message: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your message"
        )

@app.post("/run-trade")
async def trigger_trade():
    try:
        result = run_echo()
        return {"status": "success", "message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/credentials")
async def update_credentials(request: Request):
    data = await request.json()
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    save_credentials(email, password)
    return {"status": "success", "message": "Credentials saved successfully"}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 5050))
    uvicorn.run(app, host=host, port=port)