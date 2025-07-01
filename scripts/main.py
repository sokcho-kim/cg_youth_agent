import streamlit as st
import time
import random
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="서울시 청년포털 챗봇",
    page_icon="💬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #2563eb 0%, #16a34a 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
    }
    
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        min-height: 500px;
    }
    
    .quick-action-btn {
        background: linear-gradient(45deg, #3b82f6, #10b981);
        color: white;
        border: none;
        padding: 0.75rem 1rem;
        border-radius: 10px;
        margin: 0.25rem;
        cursor: pointer;
        width: 100%;
        text-align: left;
        transition: all 0.3s ease;
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    
    .info-card {
        background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin-top: 1rem;
    }
    
    .user-message {
        background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
        color: white;
        padding: 1rem;
        border-radius: 15px 15px 5px 15px;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    
    .assistant-message {
        background: #f1f5f9;
        color: #1e293b;
        padding: 1rem;
        border-radius: 15px 15px 15px 5px;
        margin: 0.5rem 0;
        margin-right: 20%;
        border-left: 4px solid #3b82f6;
    }
    
    .logo-container {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1rem;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        background: linear-gradient(45deg, #3b82f6, #10b981);
        color: white;
        padding: 0.5rem 1rem;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_started" not in st.session_state:
    st.session_state.chat_started = False

# 빠른 질문 데이터
quick_actions = [
    {"icon": "💼", "label": "일자리 정보", "question": "청년 일자리 지원 사업에 대해 알려주세요"},
    {"icon": "🎓", "label": "교육 프로그램", "question": "청년 대상 교육 프로그램이 있나요?"},
    {"icon": "❤️", "label": "복지 혜택", "question": "청년이 받을 수 있는 복지 혜택을 알려주세요"},
    {"icon": "🏠", "label": "주거 지원", "question": "청년 주거 지원 정책에 대해 설명해주세요"},
    {"icon": "📅", "label": "행사 일정", "question": "이번 달 청년 대상 행사가 있나요?"},
    {"icon": "📍", "label": "시설 안내", "question": "청년 이용 가능한 시설을 안내해주세요"},
]

# AI 응답 시뮬레이션 함수
def get_ai_response(question):
    """AI 응답을 시뮬레이션하는 함수"""
    responses = {
        "일자리": """
        🔍 **청년 일자리 지원 사업 안내**
        
        **1. 청년수당**
        - 대상: 만 18~34세 미취업 청년
        - 지원금액: 월 50만원 (최대 6개월)
        - 신청방법: 서울시 청년포털에서 온라인 신청
        
        **2. 청년일자리 도약 장려금**
        - 대상: 중소기업 취업 청년
        - 지원금액: 월 80만원 (최대 2년)
        
        **3. 청년 창업 지원**
        - 창업자금 지원: 최대 1억원
        - 멘토링 및 교육 프로그램 제공
        
        📞 문의: 02-2133-5000
        🌐 자세한 정보: youth.seoul.go.kr
        """,
        
        "교육": """
        📚 **청년 교육 프로그램 안내**
        
        **1. 청년 디지털 역량 강화**
        - AI, 빅데이터, 프로그래밍 교육
        - 무료 수강 (6개월 과정)
        
        **2. 청년 취업 아카데미**
        - 면접 스킬, 이력서 작성법
        - 직무별 전문 교육
        
        **3. 외국어 교육 지원**
        - 영어, 중국어, 일본어
        - 수강료 50% 지원
        
        📅 신청기간: 매월 1~15일
        📍 교육장소: 서울시 청년센터
        """,
        
        "복지": """
        🎁 **청년 복지 혜택 안내**
        
        **1. 청년 교통비 지원**
        - 월 교통비 15만원 한도 지원
        - 대중교통 이용 시 50% 할인
        
        **2. 청년 문화 활동 지원**
        - 공연, 전시, 영화 관람료 지원
        - 월 10만원 한도
        
        **3. 청년 건강검진 지원**
        - 종합건강검진 무료 제공
        - 정신건강 상담 서비스
        
        **4. 청년 통신비 지원**
        - 휴대폰 요금 월 2만원 지원
        
        💳 신청: 청년 복지카드 발급 후 이용
        """,
        
        "주거": """
        🏡 **청년 주거 지원 정책**
        
        **1. 청년 전세임대**
        - 지원한도: 수도권 2억원
        - 이자율: 연 1~2%
        - 임대기간: 최대 10년
        
        **2. 청년 매입임대**
        - 시세 30% 수준 임대료
        - 2년 거주 후 재계약 가능
        
        **3. 청년 주거급여**
        - 월 임대료 지원
        - 소득 기준 충족 시 지원
        
        **4. 청년 공유주택**
        - 저렴한 임대료
        - 커뮤니티 공간 제공
        
        📋 신청자격: 만 19~39세 무주택 청년
        📞 상담: 1600-3456
        """,
        
        "행사": """
        🎉 **이번 달 청년 행사 일정**
        
        **📅 12월 행사**
        
        **1. 청년 취업박람회**
        - 일시: 12월 15일(금) 10:00~17:00
        - 장소: 코엑스 A홀
        - 참여기업: 100여개 기업
        
        **2. 청년 창업 경진대회**
        - 일시: 12월 20일(수) 14:00
        - 장소: 서울시청 대회의실
        - 상금: 총 5,000만원
        
        **3. 청년 문화축제**
        - 일시: 12월 23일(토) 18:00
        - 장소: 한강공원 여의도
        - 내용: 공연, 체험부스, 푸드트럭
        
        **4. 신년 청년 네트워킹**
        - 일시: 12월 30일(토) 19:00
        - 장소: 청년센터 오픈스페이스
        
        🎫 참가신청: youth.seoul.go.kr
        """,
        
        "시설": """
        🏢 **청년 이용 시설 안내**
        
        **1. 서울시 청년센터**
        - 위치: 중구 세종대로 110
        - 시설: 스터디룸, 회의실, 카페
        - 이용시간: 09:00~22:00
        
        **2. 청년 공간 무중력지대**
        - 위치: 영등포구, 강서구 등 6개소
        - 시설: 코워킹스페이스, 메이커스페이스
        - 프로그램: 창업 지원, 네트워킹
        
        **3. 청년 도서관**
        - 위치: 각 구별 운영
        - 시설: 열람실, 스터디룸, 세미나실
        - 특별서비스: 취업 도서 코너
        
        **4. 청년 체육시설**
        - 헬스장, 수영장 할인 이용
        - 청년 스포츠클럽 운영
        
        📱 예약: 서울시 공공서비스 예약 앱
        💳 할인: 청년카드 소지 시 20% 할인
        """
    }
    
    # 키워드 기반 응답 선택
    for keyword, response in responses.items():
        if keyword in question:
            return response
    
    # 기본 응답
    return f"""
    안녕하세요! 서울시 청년포털 AI 상담사입니다. 😊
    
    **"{question}"**에 대한 답변을 준비하고 있습니다.
    
    🔍 **주요 서비스 안내**
    - 청년 일자리 지원 사업
    - 주거 지원 정책  
    - 교육 및 역량개발 프로그램
    - 복지 혜택 안내
    - 문화·여가 활동 지원
    
    더 구체적인 질문을 해주시면 정확한 정보를 안내해드리겠습니다!
    
    📞 전화상담: 02-2133-5000
    🌐 홈페이지: youth.seoul.go.kr
    """

# 메인 레이아웃
col1, col2 = st.columns([1, 3])

# 사이드바 (빠른 질문)
with col1:
    st.markdown("### 🚀 빠른 질문")
    
    for action in quick_actions:
        if st.button(f"{action['icon']} {action['label']}", key=action['label']):
            # 사용자 메시지 추가
            st.session_state.messages.append({
                "role": "user", 
                "content": action['question'],
                "timestamp": datetime.now()
            })
            
            # AI 응답 추가
            ai_response = get_ai_response(action['question'])
            st.session_state.messages.append({
                "role": "assistant", 
                "content": ai_response,
                "timestamp": datetime.now()
            })
            
            st.session_state.chat_started = True
            st.rerun()
    
    # 정보 카드
    st.markdown("""
    <div class="info-card">
        <h4>🤖 AI 청년 도우미</h4>
        <p>서울시 청년 정책, 지원사업, 일자리 정보 등을 실시간으로 안내해드립니다.</p>
        <br>
        <p><strong>💡 이용 팁</strong></p>
        <p>• 구체적인 질문일수록 정확한 답변<br>
        • 지원 자격, 신청 방법 등 상세 문의 가능<br>
        • 24시간 언제든지 이용 가능</p>
    </div>
    """, unsafe_allow_html=True)

# 메인 채팅 영역
with col2:
    # 헤더
    st.markdown("""
    <div class="main-header">
        <div class="logo-container">
            <h1>💬 서울시 청년포털 챗봇</h1>
        </div>
        <p>청년 정책과 지원사업을 쉽게 찾아보세요</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 채팅 컨테이너
    chat_container = st.container()
    
    with chat_container:
        if not st.session_state.messages:
            # 초기 환영 메시지
            st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <h2>안녕하세요! 👋</h2>
                <p>서울시 청년포털 AI 상담사입니다.<br>
                청년 정책, 지원사업, 일자리 정보 등 궁금한 것을 물어보세요!</p>
                <br>
                <div style="display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
                    <span style="background: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px;">청년수당</span>
                    <span style="background: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px;">청년일자리</span>
                    <span style="background: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px;">주거지원</span>
                    <span style="background: #e2e8f0; padding: 5px 10px; border-radius: 15px; font-size: 12px;">창업지원</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            # 채팅 메시지 표시
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>👤 나</strong><br>
                        {message["content"]}
                        <div style="font-size: 10px; opacity: 0.7; margin-top: 5px;">
                            {message["timestamp"].strftime("%H:%M")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>🤖 AI 상담사</strong><br>
                        {message["content"]}
                        <div style="font-size: 10px; opacity: 0.7; margin-top: 5px;">
                            {message["timestamp"].strftime("%H:%M")}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

# 채팅 입력
st.markdown("---")
user_input = st.chat_input("청년 정책에 대해 궁금한 것을 물어보세요...")

if user_input:
    # 사용자 메시지 추가
    st.session_state.messages.append({
        "role": "user", 
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    # 로딩 표시
    with st.spinner("답변을 준비하고 있습니다..."):
        time.sleep(1)  # 실제 API 호출 시뮬레이션
        
        # AI 응답 생성
        ai_response = get_ai_response(user_input)
        
        # AI 응답 추가
        st.session_state.messages.append({
            "role": "assistant", 
            "content": ai_response,
            "timestamp": datetime.now()
        })
    
    st.session_state.chat_started = True
    st.rerun()

# 푸터
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #64748b; font-size: 12px;">
    ⚠️ AI가 생성한 정보는 참고용이며, 정확한 정보는 공식 홈페이지를 확인해주세요.<br>
    📞 전화상담: 02-2133-5000 | 🌐 홈페이지: youth.seoul.go.kr
</div>
""", unsafe_allow_html=True)
