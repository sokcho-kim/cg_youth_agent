import os
import json
import re
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
User's Original Question: {question}

---
User's Optimized Search Query: {search_query}

---
Instructions for Answer Generation:
1. **Directness**: Address the user's question directly and clearly.
2. **Accuracy**: Base your response primarily on the "Retrieved Policy Documents." If they do not provide a direct match, you may recommend the most contextually relevant policies from within them.3. **Completeness**: Include all relevant policy details available in the documents.
3. **Completeness**: Include all relevant policy details available in the documents.
4. **User-centric**: Adapt the tone and content to the user's profile (e.g., "서울 거주 20대 미혼 여성"). If profile is missing or empty, use general language.
5. **Content Selection**: Only include the 2~3 most relevant policies in the main answer. List remaining relevant policies as a **reference list** with brief summaries if it exists.
6. **Structure**: Organize content using bullet points or numbered lists for clarity.
7. **Policy Details**: For each main policy in the answer, include:
   - 정책명 (Policy Name)
   - 설명 (Description)
   - 지원대상 (Target Beneficiaries)
   - 신청방법 (Application Method)
   - 문의 (Contact Information)
   - 관련링크 (Related Links) if available
8. **URL Inclusion Format**: If a URL is provided in the policy document, include it using the following format:  
   `<a href="URL" target="_blank">자세히 보기</a>`  
   Do not fabricate or guess URLs. Only use explicitly provided ones.
9. **Clarity**: Use easy-to-understand and concise Korean. Avoid unnecessary technical jargon.
10. **Language Requirement**: Final response must be written **in Korean only**. Do not use English or any other language.
11. **Domain Restriction**: Only respond to questions directly related to youth housing policies. If the question is irrelevant (e.g., tax, middle-aged housing, market trends), respond with a friendly message like:  
   "**죄송합니다. 저는 서울시 청년 주거 정책 전용 AI입니다. 관련된 질문만 답변드릴 수 있어요 🙇**"
12. **Icons**: Please include appropriate icons (e.g., ✅, 📌, ⚠️) to enhance clarity and readability.
13. **Personalization**: Make sure your response is accurate and helpful, accurate, and also personalize the explanation based on the user's context. Include the policy URL if it exists in the retrieved documents.
14. When there is no exact match but the user's intent is clear (e.g., "recent policies", "요즘 뭐 나왔어요?"), recommend the most contextually relevant or recently updated policies based on their profile and question type.
15. **Topic Flexibility Handling**:  
    If the user's question includes expressions like "최근", "요즘", "새로 나온", "가장 최신" and refers to general policy recommendations, provide the most recently added youth housing policies from the document list, even if they don't match the search query directly.  
    Example response:  
    > "요즘 새로 나온 청년 주거 정책을 찾고 계시는군요. 아래는 최근에 업데이트된 주요 정책입니다:"
    
    - 정책명: ...
    - 설명: ...
    - 신청방법: ...
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

def create_fallback_answer(user_profile, chat_history, question, search_query):
    # return "죄송합니다. 해당 질문에 관련된 정책 문서를 찾을 수 없습니다.", []
    # fallback 프롬프트 구성
    fallback_prompt_template = """
            너는 '서울시 청년 주거 정책 전문 AI'야. 사용자의 질문에 대해 정확하게 대응되는 정책 문서를 찾지 못했지만, 사용자의 상황이 청년 주거와 관련 있다고 판단된다면 아래 지침에 따라 유사 정책을 제안해줘.

            ---
            # USER PROFILE #
            {user_profile_data}

            # USER'S QUESTION #
            {question}

            # CHAT HISTORY #
            {chat_history}
            
            # SEARCH QUERY #
            {search_query}

            # 지침:
            1. 사용자의 질문이 전세금, 자취, 월세, 이사, 독립, 피해 등과 관련이 있으면, 주거 문제로 간주하고 반드시 응답을 생성해야 해.
            2. 정확히 일치하는 정책이 없더라도, 가장 유사하거나 도움될 수 있는 청년 주거 정책을 제안해줘.
            3. 다음 형식으로 응답해:

            안타깝지만, "{question}"에 대해 직접 지원되는 정책은 현재 없습니다.  
            하지만 다음과 같은 유사한 지원책이 도움될 수 있어요:

            - 정책명: ...
            - 설명: ...
            - 신청방법: ...
            - 문의: ...
            - 관련링크: <a href="URL" target="_blank">자세히 보기</a>

            4. 사용자의 상황에 공감하는 말투를 사용하되, 전문적이고 신뢰감 있게 말해줘.
            5. 반드시 한국어로만 응답하고, 영어는 포함하지 마.
            6. 하나의 정책만 추천해도 되지만, 최대 2~3개까지 포함할 수 있어.

            출력은 응답 본문만 자연스럽게 생성해줘. 메타 정보나 JSON 없이 대화체로 작성해.
        """
    fallback_prompt = fallback_prompt_template.format(
        user_profile_data=user_profile,
        chat_history=chat_history,
        question=question,
        search_query=search_query
    )
    fallback_answer = call_llm_via_ask(fallback_prompt)
    return fallback_answer, []


def create_qa_chain(retriever, memory, user_profile, question, search_query):
    """최종 응답을 생성하고 레퍼런스 문서도 분리해서 리턴"""
    # QA 프롬프트를 /ask API로 호출하여 답변 생성
    # 메모리에서 대화 이력 불러오기
    chat_history = memory.load_memory_variables({})["chat_history"]
    
    # 리트리버로 문서 검색 - search_query를 우선 사용하고, 없으면 question 사용
    search_terms = search_query if search_query and search_query.strip() else question
    docs = retriever.get_relevant_documents(search_terms)
    if not docs:
        return create_fallback_answer(user_profile, chat_history, question, search_query)
    
    
    # 벡터DB 검색 결과 중 상위 3개 문서 선택히여 필터링 
    top3_docs, remaining_docs = filter_documents_by_score(docs, top_n=3)
    context = "\n\n".join([doc.page_content for doc in top3_docs])

    # QA 프롬프트 구성
    prompt = QA_PROMPT.format(
        user_profile_data=user_profile,
        chat_history=chat_history,
        context=context,
        question=question,
        search_query=search_query
    )
    answer = call_llm_via_ask(prompt)

    # 메모리에 현재 질문/응답 저장
    memory.save_context({"input": question}, {"output": answer})
    
    remaining_list = []
    for doc in remaining_docs:
        # 정책명 추출
        match = re.search(r'정책명:([^\n]+)', doc.page_content)
        title = match.group(1).strip() if match else "정책 정보"
        # 관련링크 추출
        url_match = re.search(r'관련링크: *([^\n\s]+)', doc.page_content)
        url = url_match.group(1).strip() if url_match else ""
        remaining_list.append({
            "title": title,
            "url": url
        })
        
    print("remaining_list >>>> "+str(remaining_list))

    return answer, remaining_list  # 레퍼런스 문서도 분리해서 리턴

def get_active_sessions_count():
    """활성 세션 수 반환"""
    return len(session_memories)

def is_housing_policy_question(question: str) -> bool:
    # 주거 정책 질문 판단 (yes/no) 
    # 벡터DB 언어와 맞춰서 한국어로 작성 ("주거 정책", "전세자금 대출", "신혼부부" 등 키워드 접근성)
    routing_prompt = """
    아래 질문이 주거 정책과 관련된 질문인지 판단해주세요. 반드시 yes 또는 no로만 대답해주세요.

    [주거 정책 정의]
    주거 정책은 일반적으로 다음과 같은 주거 관련 지원을 포함합니다:
    - 전세자금, 월세 지원
    - 임대주택 공급
    - 자립 지원 주거
    - 신혼부부, 사회초년생 대상 주택 지원
    - 주거급여, 이사비, 보증금 등 주거비용 부담 완화

    [예시]
    Q: 전세보증금을 못 돌려받았어요 → yes  
    Q: 자취하고 싶은데 돈이 없어요 → yes  
    Q: 20대 청년 주거 지원정책이 있나요? → yes  
    Q: 신혼부부를 위한 주택 정책은 어떤 게 있어요? → yes  
    Q: 부동산 시장 전망은? → no  
    Q: 종합부동산세 줄일 수 있나요? → no  
    Q: 중장년 주거복지에 대해 알려줘 → no  

    ---
    Q: {question}
    A:
    """.strip()

    response = call_llm_via_ask(routing_prompt.format(question=question))
    return response.strip().lower().startswith("yes")

def filter_documents_by_score(docs, top_n=3):
    # 문서 필터링 함수 (벡터DB 검색 결과 중 상위 3개 문서 선택)
    sorted_docs = sorted(docs, key=lambda d: -d.metadata.get("score", 0))
    return sorted_docs[:top_n], sorted_docs[top_n:]