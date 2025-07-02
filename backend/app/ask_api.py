from fastapi import APIRouter
from pydantic import BaseModel
import openai
import os

router = APIRouter()

class AskRequest(BaseModel):
    prompt: str

@router.post("/ask")
async def ask_gpt(request: AskRequest):
    client = openai.OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": request.prompt}]
    )
    return {"response": response.choices[0].message.content} 