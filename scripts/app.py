import streamlit as st
import time

# 페이지 설정
st.set_page_config(
    page_title="서울시 청년포털 챗봇 데모",
    page_icon="💬",
    layout="wide"
)

# 간단한 스타일링
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #2563eb;
        padding: 1rem;
        background: linear-gradient(90deg, #dbeafe, #dcfce7);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 간단한 AI 응답 함수
def get_simple_response(question):
    responses = {
        "일자리": "💼 청년 일자리 지원사업: 청년수당(월 50만원), 취업장려금, 창업지원 등이 있습니다. 자세한 내용은 youth.seoul.go.kr에서 확인하세요!",
        "교육": "📚 청년 교육 프로그램: 디지털 역량 강화, 취업 아카데미, 외국어 교육 지원 등을 제공합니다.",
        "복지": "🎁 청년 복지 혜택: 교통비 지원, 문화활동 지원, 건강검진, 통신비 지원 등 다양한 혜택이 있습니다.",
        "주거": "🏠 청년 주거 지원: 전세임대, 매입임대, 주거급여, 공유주택 등 주거 안정을 위한 정책을 지원합니다.",
        "행사": "🎉 청년 행사: 취업박람회, 창업경진대회, 문화축제, 네트워킹 행사 등이 정기적으로 열립니다.",
        "시설": "🏢 청년 시설: 청년센터, 무중력지대, 청년도서관, 체육시설 등을 이용할 수 있습니다."
    }
    
    for key, response in responses.items():
        if key in question:
            return response
    
    return f"안녕하세요! 서울시 청년포털 AI 상담사입니다. '{question}'에 대한 정보를 찾고 있습니다. 일자리, 교육, 복지, 주거, 행사, 시설 관련 질문을 해보세요! 📞 문의: 02-2133-5000"

# 메인 타이틀
st.markdown("""
<div class="main-title">
    <h1>💬 서울시 청년포털 챗봇 데모</h1>
    <p>청년 정책과 지원사업을 쉽게 찾아보세요</p>
</div>
""", unsafe_allow_html=True)

# 사이드바 - 빠른 질문
with st.sidebar:
    st.header("🚀 빠른 질문")
    
    quick_questions = [
        "💼 일자리 정보가 궁금해요",
        "📚 교육 프로그램 알려주세요", 
        "🎁 복지 혜택이 뭐가 있나요",
        "🏠 주거 지원 정책 설명해주세요",
        "🎉 이번 달 행사 일정 알려주세요",
        "🏢 이용 가능한 시설 안내해주세요"
    ]
    
    for question in quick_questions:
        if st.button(question, key=question):
            # 사용자 메시지 추가
            st.session_state.messages.append({"role": "user", "content": question})
            # AI 응답 추가
            response = get_simple_response(question)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    st.markdown("---")
    st.info("🤖 AI 청년 도우미\n\n서울시 청년 정책 정보를 안내해드립니다!")

# 메인 채팅 영역
st.subheader("💬 채팅")

# 채팅 메시지 표시
if st.session_state.messages:
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("assistant").write(message["content"])
else:
    # 초기 메시지
    st.chat_message("assistant").write("""
    안녕하세요! 👋 서울시 청년포털 AI 상담사입니다.
    
    **무엇을 도와드릴까요?**
    - 청년 일자리 지원 사업
    - 교육 및 역량개발 프로그램  
    - 복지 혜택 안내
    - 주거 지원 정책
    - 행사 및 시설 정보
    
    왼쪽 사이드바의 빠른 질문을 클릭하거나 아래에 직접 질문해보세요!
    """)

# 채팅 입력
if prompt := st.chat_input("질문을 입력하세요..."):
    # 사용자 메시지 표시 및 저장
    st.chat_message("user").write(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # AI 응답 생성 및 표시
    with st.chat_message("assistant"):
        with st.spinner("답변 준비 중..."):
            time.sleep(1)  # 응답 지연 시뮬레이션
            response = get_simple_response(prompt)
            st.write(response)
    
    # AI 응답 저장
    st.session_state.messages.append({"role": "assistant", "content": response})

# 푸터
st.markdown("---")
st.caption("⚠️ 데모 버전입니다. 실제 정보는 youth.seoul.go.kr에서 확인하세요.")
