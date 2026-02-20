from fastapi import FastAPI, HTTPException, Header
from pymongo import MongoClient
from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Database Setup
client = MongoClient(os.getenv("MONGO_CONNECTION_STRING"))
db = client["TravelWAI"]

class TravelPlan(BaseModel):
    user_prompt: str
    agent_response: str
    evaluation_score: int

@app.post("/v1/save-plan")
async def save_plan(plan: TravelPlan, x_api_key: str = Header(None)):
    # Simple Security Check
    if x_api_key != os.getenv("INTERNAL_API_KEY"):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    collection = db["Plans"]
    result = collection.insert_one(plan.dict())
    return {"status": "success", "id": str(result.inserted_id)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)