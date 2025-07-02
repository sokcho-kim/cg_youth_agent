from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import CharacterTextSplitter
from langchain.schema import Document

import os
import json
import openai
from dotenv import load_dotenv

# .env 파일 로드 (개발환경용)
load_dotenv()

# ChromaDB 텔레메트리 비활성화
os.environ["ANONYMIZED_TELEMETRY"] = "False"

app = FastAPI(title="Youth Policy RAG Server", version="1.0.0")

# CORS 허용 (프론트엔드와 연동 위해)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 환경 변수에서 OpenAI API 키 로드
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

# LLM/RAG 사용 가능 여부 플래그
rag_enabled = True
try:
    # 간단한 API Key 유효성 체크 (openai 라이브러리 사용 시 에러 발생 방지)
    if not OPENAI_API_KEY or OPENAI_API_KEY == "YOUR_OPENAI_API_KEY":
        rag_enabled = False
except Exception:
    rag_enabled = False

def load_policy_data():
    """정책 데이터를 로드하고 Document 객체로 변환 (text 필드만 사용)"""
    try:
        DATA_PATH = os.path.join(os.path.dirname(__file__), '../data/seoul_youth_policies_with_url_rag.jsonl')
        if not os.path.exists(DATA_PATH):
            print(f"Warning: Data file not found at {DATA_PATH}")
            return []
        documents = []
        with open(DATA_PATH, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    doc_data = json.loads(line.strip())
                    policy_text = doc_data.get('text', '')
                    document = Document(
                        page_content=policy_text,
                        metadata={
                            'id': doc_data.get('id', ''),
                            'category': doc_data.get('category', ''),
                            'source': 'seoul_youth_policies_with_url_rag'
                        }
                    )
                    documents.append(document)
                except json.JSONDecodeError as e:
                    print(f"Error parsing line {line_num}: {e}")
                    continue
        print(f"Successfully loaded {len(documents)} policy documents")
        return documents
    except Exception as e:
        print(f"Error loading policy data: {e}")
        return []

def initialize_vectorstore():
    """벡터스토어 초기화 및 데이터 로드"""
    try:
        embeddings = OpenAIEmbeddings()
        persist_directory = os.path.join(os.path.dirname(__file__), '../chroma_db')
        
        # 기존 벡터스토어가 있는지 확인
        if os.path.exists(persist_directory):
            print("Loading existing vectorstore...")
            try:
                vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
                collection = vectorstore._collection
                if collection.count() > 0:
                    print(f"Found {collection.count()} existing documents in vectorstore")
                    return vectorstore
            except Exception as e:
                print(f"Error loading existing vectorstore: {e}")
                print("Creating new vectorstore...")
        
        # 새로운 벡터스토어 생성
        print("Creating new vectorstore...")
        documents = load_policy_data()
        
        if not documents:
            print("No documents loaded. Creating empty vectorstore.")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=200, separator="\n")
            split_docs = text_splitter.split_documents(documents)
            print(f"Split documents into {len(split_docs)} chunks")
            
            try:
                vectorstore = Chroma.from_documents(
                    documents=split_docs,
                    embedding=embeddings,
                    persist_directory=persist_directory
                )
                vectorstore.persist()
                print(f"Vectorstore created with {len(split_docs)} document chunks")
            except Exception as e:
                print(f"Error creating vectorstore with embeddings: {e}")
                print("Creating empty vectorstore without embeddings...")
                vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        
        return vectorstore
        
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        print("Creating empty vectorstore as fallback...")
        try:
            persist_directory = os.path.join(os.path.dirname(__file__), '../chroma_db')
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=None)
            return vectorstore
        except Exception as fallback_error:
            print(f"Fallback vectorstore creation failed: {fallback_error}")
            return None

# 벡터스토어 및 Retriever 초기화
print("Initializing vectorstore...")
vectorstore = initialize_vectorstore()

if vectorstore is None:
    print("Warning: Vectorstore initialization failed. RAG functionality will be disabled.")
    retriever = None
    rag_enabled = False
else:
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# LLM 초기화
llm = None
if rag_enabled:
    llm = ChatOpenAI(model_name="gpt-4o", temperature=0)

# 세션별 대화 메모리 저장소 (개발용: 실제 서비스에서는 외부 DB 사용)
session_memories = {}

# 사용자 정보 저장소 (개발용: 실제 서비스에서는 DB 사용)
# key: session_id, value: {"user_profile": "대학생", "some_other_info": "값"}
user_profiles_db = {}

# User information extraction prompt (English for better performance)
initial_analysis_prompt_template = """
You are an expert policy analyst. Analyze the user's request and extract the following information:

1. residence: User's residence (e.g., "Seoul", "Gyeonggi", "Other regions")
2. age: User's age (number or age group like "20s", "30s")
3. gender: User's gender ("Male", "Female", "Other", "Not specified")
4. marital_status: Marital status ("Married", "Single", "Not specified")
5. user_profile: Korean summary combining the above info (e.g., "서울 거주 20대 미혼 여성")
6. policy_area_of_interest: Policy area of interest (e.g., "Housing", "Employment", "Welfare", "Education")
7. specific_keywords: Important keywords from the user's question
8. optimized_search_query: Most effective query for policy search

Output as JSON. Leave empty string if information is not available.

---
User's Request: {user_input}
"""
initial_analysis_llm = ChatOpenAI(model_name="gpt-4o", temperature=0.1)
initial_analysis_prompt = PromptTemplate.from_template(initial_analysis_prompt_template)

# Enhanced QA prompt for better RAG performance
qa_prompt_template = """You are a knowledgeable and empathetic policy assistant specializing in Korean government policies. Provide accurate, comprehensive, and user-centric information based ONLY on the provided policy documents and chat history.

---
# USER PROFILE #
User's Profile: {user_profile_data}
---
Chat History:
{chat_history}

---
Retrieved Policy Documents:
{context}

---
User's Question: {question}

---
Instructions for Answer Generation:
1. **Directness**: Address the user's question directly and clearly.
2. **Accuracy**: Strictly use information from the "Retrieved Policy Documents." Do NOT make up information. If the answer is not in the documents, state that you cannot find relevant information.
3. **Completeness**: Provide comprehensive answers covering all relevant aspects found in the documents.
4. **User-centric**: Tailor your response to the user's specific profile (e.g., "서울 거주 20대 미혼 여성"). If 'User Profile' is '정보 없음' or empty, use general language.
5. **Structure**: Organize information clearly using bullet points or numbered lists when beneficial.
6. **Policy Details**: When discussing policies, include:
   - Policy name (정책명)
   - Description (설명)
   - Target beneficiaries (지원대상)
   - Application method (신청방법)
   - Contact information (문의)
   - Related links (관련링크) if available
7. **URL Inclusion**: Include relevant policy URLs at the end, clearly labeled as "자세히 보기:" or "관련 정책 URL:". Do not invent URLs.
8. **Clarity**: Use clear, concise, and easy-to-understand Korean language. Avoid jargon when possible.

Helpful and Tailored Answer:
"""
QA_PROMPT = PromptTemplate.from_template(qa_prompt_template)

# --- FastAPI 엔드포인트 ---

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
    return {
        "status": "healthy", 
        "vectorstore_docs": vectorstore._collection.count(),
        "active_sessions": len(session_memories)
    }

@app.post("/chat")
async def chat_with_bot(request: ChatRequest):
    if not rag_enabled:
        return {"response": "[오류] OpenAI API Key가 설정되어 있지 않거나 벡터스토어 초기화에 실패하여 AI 답변 기능이 비활성화되어 있습니다. 환경 변수 OPENAI_API_KEY를 설정해주세요."}
    
    if retriever is None:
        return {"response": "[오류] 벡터스토어가 초기화되지 않아 RAG 기능을 사용할 수 없습니다."}
    
    session_id = request.session_id
    user_message = request.user_message

    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=5)
    memory = session_memories[session_id]

    current_user_profile = user_profiles_db.get(session_id, {}).get("user_profile", "정보 없음")

    if current_user_profile == "정보 없음":
        try:
            analysis_chain = initial_analysis_prompt | initial_analysis_llm
            analysis_response = analysis_chain.invoke({"user_input": user_message}).content
            initial_info = json.loads(analysis_response)

            extracted_profile = initial_info.get("user_profile")
            if extracted_profile and extracted_profile != "정보 없음":
                user_profiles_db[session_id] = user_profiles_db.get(session_id, {})
                user_profiles_db[session_id]["user_profile"] = extracted_profile
                current_user_profile = extracted_profile

            search_query_from_analysis = initial_info.get("optimized_search_query", user_message)
        except json.JSONDecodeError:
            print("Warning: Initial analysis did not return valid JSON.")
            search_query_from_analysis = user_message
        except Exception as e:
            print(f"Error during initial analysis: {e}")
            search_query_from_analysis = user_message
    else:
        try:
            analysis_chain = initial_analysis_prompt | initial_analysis_llm
            analysis_response = analysis_chain.invoke({"user_input": user_message}).content
            initial_info = json.loads(analysis_response)
            search_query_from_analysis = initial_info.get("optimized_search_query", user_message)
        except (json.JSONDecodeError, Exception):
            search_query_from_analysis = user_message

    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        combine_docs_chain_kwargs={
            "prompt": QA_PROMPT,
            "template_extra_variables": {"user_profile_data": current_user_profile}
        }
    )

    try:
        response = qa_chain.invoke({"question": user_message})
        return {"response": response["answer"]}
    except Exception as e:
        print(f"[OpenAI API Error] {e}")
        return {"response": "[오류] 일시적으로 AI 답변이 불가합니다. 네트워크 또는 OpenAI 서버 연결 문제일 수 있습니다."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 