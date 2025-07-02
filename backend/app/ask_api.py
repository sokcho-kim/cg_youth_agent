from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os

router = APIRouter()

class AskRequest(BaseModel):
    prompt: str

@router.post("/ask")
async def ask_gpt(request: AskRequest):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": request.prompt}]
    )
    return {"response": response.choices[0].message["content"]} 