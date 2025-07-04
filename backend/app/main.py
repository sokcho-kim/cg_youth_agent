# 실행 방법 (로컬):
# cd backend
# python -m app.main

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import os
import json
from dotenv import load_dotenv
from .ask_api import router as ask_router

# .env 파일 로드 (개발환경용)
load_dotenv()

# ChromaDB 텔레메트리 비활성화
os.environ["ANONYMIZED_TELEMETRY"] = "False"
# 모듈 import
from .dataLoader import get_vectorstore_and_retriever
from .llm_manager import (
    get_or_create_memory, 
    extract_user_profile, 
    create_qa_chain, 
    get_active_sessions_count,
    is_housing_policy_question,
    filter_documents_by_score  
)

app = FastAPI(title="Youth Policy RAG Server", version="1.0.0")
app.include_router(ask_router)

# CORS 허용 (프론트엔드와 연동 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 벡터스토어 및 리트리버 초기화
vectorstore, retriever, vectorstore_enabled = get_vectorstore_and_retriever()

class ChatRequest(BaseModel):
    session_id: str
    user_message: str

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "message": "Youth Policy RAG Server",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health_check():
    """서버 상태 확인"""
    vectorstore_docs = 0
    if vectorstore and hasattr(vectorstore, '_collection'):
        try:
            vectorstore_docs = vectorstore._collection.count()
        except:
            vectorstore_docs = 0
    
    return {
        "status": "healthy", 
        "vectorstore_docs": vectorstore_docs,
        "active_sessions": get_active_sessions_count(),
        "rag_enabled": vectorstore_enabled
    }

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    if retriever is None:
        return {"response": "[오류] 벡터스토어가 초기화되지 않아 RAG 기능을 사용할 수 없습니다."}
    
    session_id = request.session_id
    user_message = request.user_message

    # Step 1: 주거 정책 관련 질문 여부 판단
    if not is_housing_policy_question(user_message):
        return {
            "response": "저는 서울시 청년 주거 정책 전문 AI입니다. 관련된 질문만 답변드릴 수 있어요 🙇‍♀️"
        }

    # Step 2: 사용자 프로필 및 메모리 처리
    # 세션별 메모리 가져오기
    memory = get_or_create_memory(session_id)

    # 사용자 프로필 추출
    current_user_profile, search_query_from_analysis = extract_user_profile(user_message, session_id)

    # Step 3: QA 체인 생성 및 답변 생성 (llm 인자 제거) + 문서 목록 분리
    try:
        answer, remaining_docs = create_qa_chain(retriever, memory, current_user_profile, user_message)
        remaining_list = [
            doc.metadata.get("category") or doc.metadata.get("id") or doc.page_content[:30] for doc in remaining_docs
        ]
        return {"response": answer, "remaining_docs": remaining_list}
    except Exception as e:
        print(f"[OpenAI API Error] {e}")
        return {"response": "[오류] 일시적으로 AI 답변이 불가합니다. 네트워크 또는 OpenAI 서버 연결 문제일 수 있습니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000) 