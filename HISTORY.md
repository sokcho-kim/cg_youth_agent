# 프로젝트 변경 이력 (History)

## 주요 변경사항

### 2024-07-02
- 백엔드 `/ask` API 신설 (OpenAI GPT-4o 직접 호출)
- GPT 키는 Render 서버 환경변수에서만 관리, 코드/프론트엔드/깃허브에는 노출되지 않음
- 프론트엔드에서 모든 GPT 호출은 `/ask` API를 통해서만 가능하도록 구조 개선
- README에 API 서버 고정 주소(`https://youth-chatbot-backend.onrender.com/`) 명시
- 프론트엔드 환경변수 및 예시 코드 일괄 수정

---

## /ask API 사용법

### 1. 백엔드 (FastAPI)
- 엔드포인트: `POST /ask`
- 요청 예시:
```json
{
  "prompt": "GPT에게 보낼 프롬프트 내용"
}
```
- 응답 예시:
```json
{
  "response": "GPT가 생성한 답변"
}
```

### 2. 프론트엔드 (Next.js)
- 예시 코드:
```js
const response = await fetch("https://youth-chatbot-backend.onrender.com/ask", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ prompt: "안녕 GPT!" }),
});
const data = await response.json();
console.log(data.response);
```
- 또는 Next.js API 라우트(`/api/ask`)를 통해 프록시 가능

---

## 기타
- 모든 LLM 호출은 반드시 `/ask` API를 통해야 하며, GPT 키는 서버에만 존재합니다.
- 정책 챗봇(RAG)은 `/chat` 엔드포인트를 사용합니다. 