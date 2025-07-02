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
os.environ["OPENAI_API_KEY"] = "YOUR_OPENAI_API_KEY"

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
        # 임베딩 모델 초기화
        embeddings = OpenAIEmbeddings()
        
        # 벡터스토어 경로 설정
        persist_directory = os.path.join(os.path.dirname(__file__), '../chroma_db')
        
        # 기존 벡터스토어가 있는지 확인
        if os.path.exists(persist_directory):
            print("Loading existing vectorstore...")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
            
            # 기존 데이터가 있는지 확인
            collection = vectorstore._collection
            if collection.count() > 0:
                print(f"Found {collection.count()} existing documents in vectorstore")
                return vectorstore
        
        # 새로운 벡터스토어 생성
        print("Creating new vectorstore...")
        
        # 정책 데이터 로드
        documents = load_policy_data()
        
        if not documents:
            print("No documents loaded. Creating empty vectorstore.")
            vectorstore = Chroma(persist_directory=persist_directory, embedding_function=embeddings)
        else:
            # 텍스트 분할
            text_splitter = CharacterTextSplitter(
                chunk_size=1000, 
                chunk_overlap=200,
                separator="\n"
            )
            split_docs = text_splitter.split_documents(documents)
            print(f"Split documents into {len(split_docs)} chunks")
            
            # 벡터스토어 생성
            vectorstore = Chroma.from_documents(
                documents=split_docs,
                embedding=embeddings,
                persist_directory=persist_directory
            )
            
            # 벡터스토어 저장
            vectorstore.persist()
            print(f"Vectorstore created with {len(split_docs)} document chunks")
        
        return vectorstore
        
    except Exception as e:
        print(f"Error initializing vectorstore: {e}")
        raise

# 벡터스토어 및 Retriever 초기화
print("Initializing vectorstore...")
vectorstore = initialize_vectorstore()
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# LLM 초기화
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
    session_id = request.session_id
    user_message = request.user_message

    # 1. 세션별 대화 메모리 가져오기 (WindowMemory 사용)
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferWindowMemory(memory_key="chat_history", return_messages=True, k=5) # 최근 5개 대화 유지
    memory = session_memories[session_id]

    # 2. 사용자 정보 가져오기 (DB/저장소에서)
    # 로그인 정보나 DB에 저장된 사용자 프로필이 있는 경우
    current_user_profile = user_profiles_db.get(session_id, {}).get("user_profile", "정보 없음")

    # 3. 사용자 메시지에서 정보 추출 및 사용자 프로필 업데이트 (선택적)
    # user_profiles_db에 사용자 정보가 없거나, 새로운 정보가 메시지에 포함된 경우
    if current_user_profile == "정보 없음":
        try:
            analysis_chain = initial_analysis_prompt | initial_analysis_llm
            analysis_response = analysis_chain.invoke({"user_input": user_message}).content
            initial_info = json.loads(analysis_response)

            extracted_profile = initial_info.get("user_profile")
            if extracted_profile and extracted_profile != "정보 없음": # 유의미한 정보가 추출된 경우
                # 사용자 프로필 DB 업데이트
                user_profiles_db[session_id] = user_profiles_db.get(session_id, {})
                user_profiles_db[session_id]["user_profile"] = extracted_profile
                current_user_profile = extracted_profile # 현재 답변에 반영

            search_query_from_analysis = initial_info.get("optimized_search_query", user_message)
        except json.JSONDecodeError:
            print("Warning: Initial analysis did not return valid JSON.")
            search_query_from_analysis = user_message
        except Exception as e:
            print(f"Error during initial analysis: {e}")
            search_query_from_analysis = user_message
    else:
        # 이미 사용자 정보가 있는 경우, 검색 쿼리만 최적화하거나 원본 메시지 사용
        try:
            analysis_chain = initial_analysis_prompt | initial_analysis_llm
            analysis_response = analysis_chain.invoke({"user_input": user_message}).content
            initial_info = json.loads(analysis_response)
            search_query_from_analysis = initial_info.get("optimized_search_query", user_message)
        except (json.JSONDecodeError, Exception):
            search_query_from_analysis = user_message

    # 4. ConversationalRetrievalChain 설정
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        memory=memory,
        # condense_question_prompt는 기본값을 사용하거나 별도 정의
        combine_docs_chain_kwargs={
            "prompt": QA_PROMPT,
            # 'user_profile_data' 변수에 현재 사용자 프로필 주입
            "template_extra_variables": {"user_profile_data": current_user_profile}
        }
    )

    # 5. 챗봇 답변 생성
    response = qa_chain.invoke({"question": user_message}) # 여기서 question은 사용자의 원본 메시지

    # 최종 답변 반환
    return {"response": response["answer"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 