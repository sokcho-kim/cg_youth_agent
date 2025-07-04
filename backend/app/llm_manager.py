import os
import json
import requests
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationalRetrievalChain
from langchain_chroma import Chroma
from app.ask_api import run_llm

# LLM 호출을 /ask API로만 수행
ASK_API_URL = os.environ.get("ASK_API_URL", "https://youth-chatbot-backend.onrender.com/ask")

# def call_llm_via_ask(prompt: str) -> str:
#     response = requests.post(ASK_API_URL, json={"prompt": prompt})
#     response.raise_for_status()
#     return response.json()["response"]

def call_llm_via_ask(prompt: str) -> str:
    return run_llm(prompt)

# 세션별 대화 메모리 저장소 (개발용: 실제 서비스에서는 외부 DB 사용)
session_memories = {}

# 사용자 정보 저장소 (개발용: 실제 서비스에서는 DB 사용)
# key: session_id, value: {"user_profile": "대학생", "some_other_info": "값"}
user_profiles_db = {}

# User information extraction prompt (English for better performance)
initial_analysis_prompt_template = """
You are an expert policy analyst. Analyze the user's request and extract the following information. Respond in JSON format only:

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
qa_prompt_template = """You are a knowledgeable and empathetic policy assistant specializing in **Korean youth housing policies**. You MUST respond in Korean language only. Provide accurate, comprehensive, and user-centric information based ONLY on the provided policy documents and chat history.

⚠️ 당신은 서울시 청년 주거 정책 전용 AI입니다. 다음 지침을 철저히 따르세요.

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
1. **Domain Restriction**: Only respond to questions directly related to youth housing policies. If the question is irrelevant (e.g., tax, middle-aged housing, market trends), respond with a friendly message like:  
   "**죄송합니다. 저는 서울시 청년 주거 정책 전용 AI입니다. 관련된 질문만 답변드릴 수 있어요 🙇**"
2. **Directness**: Address the user's question directly and clearly.
3. **Accuracy**: Use information strictly from the "Retrieved Policy Documents." Do NOT fabricate or infer missing information.
4. **Completeness**: Include all relevant policy details available in the documents.
5. **User-centric**: Adapt the tone and content to the user's profile (e.g., "서울 거주 20대 미혼 여성"). If profile is missing or empty, use general language.
6. **Content Selection**: Only include the 2~3 most relevant policies in the main answer. List remaining relevant policies as a **reference list** with brief summaries.
7. **Structure**: Organize content using bullet points or numbered lists for clarity.
8. **Policy Details**: For each main policy in the answer, include:
   - 정책명 (Policy Name)
   - 설명 (Description)
   - 지원대상 (Target Beneficiaries)
   - 신청방법 (Application Method)
   - 문의 (Contact Information)
   - 관련링크 (Related Links) if available
9. **URL Inclusion Format**: If a URL is provided in the policy document, include it using the following format:  
   `<a href="URL" target="_blank">자세히 보기</a>`  
   Do not fabricate or guess URLs. Only use explicitly provided ones.
10. **Clarity**: Use easy-to-understand and concise Korean. Avoid unnecessary technical jargon.
11. **Language Requirement**: Final response must be written **in Korean only**. Do not use English or any other language.

Provide a helpful, accurate, and strictly domain-specific response. Include the policy URL if it exists in the retrieved documents.
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
    """최종 응답을 생성하고 레퍼런스 문서도 분리해서 리턴"""
    # QA 프롬프트를 /ask API로 호출하여 답변 생성
    # 메모리에서 대화 이력 불러오기
    chat_history = memory.load_memory_variables({})["chat_history"]
    
    # 리트리버로 문서 검색
    docs = retriever.get_relevant_documents(question) 
    if not docs:
        return "죄송합니다. 해당 질문에 관련된 정책 문서를 찾을 수 없습니다.", []
    
    # 벡터DB 검색 결과 중 상위 3개 문서 선택히여 필터링 
    top3_docs, remaining_docs = filter_documents_by_score(docs, top_n=3)
    context = "\n\n".join([doc.page_content for doc in top3_docs])

    # QA 프롬프트 구성
    prompt = QA_PROMPT.format(
        user_profile_data=user_profile,
        chat_history=chat_history,
        context=context,
        question=question
    )
    answer = call_llm_via_ask(prompt)

    # 메모리에 현재 질문/응답 저장
    memory.save_context({"input": question}, {"output": answer})
    return answer, remaining_docs  # 레퍼런스 문서도 분리해서 리턴

def get_active_sessions_count():
    """활성 세션 수 반환"""
    return len(session_memories)

def is_housing_policy_question(question: str) -> bool:
    # 청년 주거 정책 질문 판단 (yes/no) 
    # 벡터DB 언어와 맞춰서 한국어로 작성 ("청년 주거 정책", "전세자금 대출", "신혼부부" 등 키워드 접근성)
    routing_prompt = """
    // Task
    입력된 question이 "청년 주거 정책"과 관련된 질문인지 판단해주세요.
    answer는 반드시 "yes" 또는 "no"로만 해주세요.

    // Context
    청년 주거 정책은 청년층(만 19~39세)을 대상으로 하는 주거 지원 정책을 의미합니다.
    예: 청년 전세자금 대출, 청년 임대주택, 신혼부부 주택 등

    ---
    question: {question}
    answer:""".strip()

    response = call_llm_via_ask(routing_prompt.format(question=question))
    return response.strip().lower().startswith("yes")

def filter_documents_by_score(docs, top_n=3):
    # 문서 필터링 함수 (벡터DB 검색 결과 중 상위 3개 문서 선택)
    sorted_docs = sorted(docs, key=lambda d: -d.metadata.get("score", 0))
    return sorted_docs[:top_n], sorted_docs[top_n:]