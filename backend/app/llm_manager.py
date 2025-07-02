import os
import json
import requests
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_chroma import Chroma

# LLM 호출을 /ask API로만 수행
ASK_API_URL = os.environ.get("ASK_API_URL", "https://youth-chatbot-backend.onrender.com/ask")

def call_llm_via_ask(prompt: str) -> str:
    response = requests.post(ASK_API_URL, json={"prompt": prompt})
    response.raise_for_status()
    return response.json()["response"]

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

def get_or_create_memory(session_id):
    """세션별 메모리를 가져오거나 새로 생성"""
    if session_id not in session_memories:
        session_memories[session_id] = ConversationBufferWindowMemory(
            memory_key="chat_history", 
            return_messages=True, 
            k=5
        )
    return session_memories[session_id]

def extract_user_profile(user_message, session_id):
    """사용자 메시지에서 프로필 정보 추출"""
    current_user_profile = user_profiles_db.get(session_id, {}).get("user_profile", "정보 없음")
    
    if current_user_profile == "정보 없음":
        try:
            prompt = initial_analysis_prompt.format(user_input=user_message)
            analysis_response = call_llm_via_ask(prompt)
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
            prompt = initial_analysis_prompt.format(user_input=user_message)
            analysis_response = call_llm_via_ask(prompt)
            initial_info = json.loads(analysis_response)
            search_query_from_analysis = initial_info.get("optimized_search_query", user_message)
        except (json.JSONDecodeError, Exception):
            search_query_from_analysis = user_message
    
    return current_user_profile, search_query_from_analysis

def create_qa_chain(retriever, memory, user_profile, question):
    # QA 프롬프트를 /ask API로 호출하여 답변 생성
    prompt = QA_PROMPT.format(
        user_profile_data=user_profile,
        chat_history="",  # 필요시 메모리에서 가져와서 추가
        context="",        # 필요시 retriever에서 가져와서 추가
        question=question
    )
    answer = call_llm_via_ask(prompt)
    return answer

def get_active_sessions_count():
    """활성 세션 수 반환"""
    return len(session_memories)