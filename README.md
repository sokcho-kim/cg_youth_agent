# 청년정보통 챗봇

서울시 청년 정책 정보를 제공하는 AI 챗봇 서비스입니다.

## 📦 프로젝트 구조

```
📦 youth_chatbot/
├── frontend/   ← React/Next.js (Vercel 배포)
├── backend/    ← FastAPI + LangChain (Render 배포)
└── README.md
```

## 🚀 빠른 시작

### Backend 실행 (로컬 개발)

```bash
cd backend
pip install -r requirements.txt
python run.py
```

- FastAPI 서버: http://localhost:8000
- API 문서: http://localhost:8000/docs
- 헬스체크: http://localhost:8000/health

### Frontend 실행 (로컬 개발)

#### 필수 요구사항
- **Node.js**: 18.19.0 (LTS 버전 권장)
- **npm**: 9.x 이상

#### 설치 및 실행
```bash
cd frontend
npm install
npm run dev
```

- Next.js 앱: http://localhost:3000

#### Node.js 버전 관리 (권장)
```bash
# nvm-windows 설치 후
nvm install 18.19.0
nvm use 18.19.0
```

## 🔧 문제 해결

### Node.js 버전 문제
- **문제**: Node.js 22.x에서 일부 패키지 호환성 문제 발생
- **해결**: Node.js 18.19.0 (LTS) 사용 권장

### 의존성 설치 문제
- **문제**: SSL/TLS 오류 또는 권한 문제
- **해결**: 
  ```bash
  npm cache clean --force
  npm config set strict-ssl false
  npm install --legacy-peer-deps
  ```


## 🏗️ 아키텍처

### Backend (FastAPI + LangChain)
- **FastAPI**: REST API 서버
- **LangChain**: RAG (Retrieval-Augmented Generation) 체인
- **ChromaDB**: 벡터 데이터베이스
- **OpenAI GPT-4**: LLM 모델

### Frontend (Next.js)
- **React 19**: UI 프레임워크
- **Next.js 15.2.4**: 풀스택 프레임워크
- **Tailwind CSS**: 스타일링
- **shadcn/ui**: UI 컴포넌트
- **Radix UI**: 접근성 컴포넌트

## 🗂️ 데이터 구조

### 정책 데이터 (`backend/data/seoul_youth_policies_with_url_rag.jsonl`)
```json
{
  "id": "policy_001",
  "category": "주택공급",
  "text": "정책명: 청년안심주택\n설명: ...\n지원대상: ...\n신청방법: ...\n문의: ...\n관련링크: ..."
}
```

## 🤖 AI 기능

### 사용자 정보 추출
챗봇이 사용자 메시지에서 다음 정보를 자동으로 추출합니다:
- **거주지**: 서울, 경기, 기타 지역 등
- **연령**: 숫자 또는 '20대', '30대' 등
- **성별**: 남성/여성/기타/미기재
- **결혼여부**: 기혼/미혼/미기재
- **user_profile**: 위 정보를 조합한 한글 요약 (예: '서울 거주 20대 미혼 여성')

### 맞춤형 답변
추출된 사용자 정보를 바탕으로 개인화된 정책 추천을 제공합니다.

## 🚀 배포

### Backend (Render)
```bash
# Render 대시보드에서 새 Web Service 생성
# Build Command: pip install -r requirements.txt
# Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Frontend (Vercel)
```bash
# Vercel 대시보드에서 새 프로젝트 생성
# Framework Preset: Next.js
# Root Directory: frontend
```

## 🔧 환경 변수

### Backend
```env
OPENAI_API_KEY=your_openai_api_key_here
```

### Frontend
```env
NEXT_PUBLIC_API_URL=https://youth-chatbot-backend.onrender.com  # 프로덕션
```

## 🛠️ 개발 가이드

### 새로운 정책 데이터 추가
1. `backend/data/` 폴더에 JSONL 파일 추가
2. `backend/app/main.py`의 `load_policy_data()` 함수에서 경로 수정
3. 서버 재시작

### UI 수정
1. `frontend/app/page.tsx`에서 메인 페이지 수정
2. `frontend/components/`에서 컴포넌트 수정
3. `frontend/app/globals.css`에서 스타일 수정

### 패키지 관리
```bash
# 새 패키지 추가
npm install package-name

# 개발 의존성 추가
npm install --save-dev package-name

# 패키지 제거
npm uninstall package-name
```

## 📝 API 문서

### POST /chat
```json
{
  "session_id": "string",
  "user_message": "string"
}
```

### Response
```json
{
  "response": "string"
}
```

## 🔍 주요 기능
- ✅ 사용자 정보 자동 추출 (거주지, 연령, 성별, 결혼여부)
- ✅ 맞춤형 정책 추천
- ✅ RAG 기반 정확한 답변
- ✅ 세션별 대화 메모리
- ✅ 실시간 채팅 인터페이스
- ✅ 반응형 디자인
- ✅ 접근성 지원

