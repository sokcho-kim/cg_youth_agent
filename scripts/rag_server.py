from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import os
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain.llms import OpenAI
from langchain.chains import RetrievalQA

app = FastAPI()

# CORS 허용 (프론트엔드와 연동 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 데이터 로드 및 벡터화
DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/seoul_youth_policies_categorized.jsonl')
with open(DATA_PATH, "r", encoding="utf-8") as f:
    docs = [json.loads(line) for line in f]

# 정책 설명만 추출
texts = [
    f"정책명: {doc['policy_name']}\n설명: {doc['description']}\n대상: {doc['eligible_targets']}\n신청: {doc['application']}\n문의: {doc['inquiry']}"
    for doc in docs
]

# 텍스트 분할
text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
split_texts = text_splitter.create_documents(texts)

# 벡터스토어 생성
embeddings = OpenAIEmbeddings()  # OPENAI_API_KEY 필요
vectorstore = FAISS.from_documents(split_texts, embeddings)

# RAG 체인
qa = RetrievalQA.from_chain_type(
    llm=OpenAI(temperature=0),
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
async def chat(req: ChatRequest):
    answer = qa.run(req.question)
    return {"answer": answer} 