export const maxDuration = 30

export async function POST(req: Request) {
  const { question } = await req.json();
  
  // 타입 및 값 확인
  console.log("question type:", typeof question, "value:", question);

  // fallback: string이 아니면 빈 문자열로 대체
  let safeQuestion = question;
  if (typeof question !== "string") {
    console.error("[Error] question must be a string. Fallback to empty string.");
    safeQuestion = "";
  }

  // 배포된 백엔드 URL로 고정
  const backendUrl = "https://youth-chatbot-backend.onrender.com";
  
  // 백엔드 API 형식에 맞게 요청 데이터 구성
  const requestData = {
    session_id: "default_session", // 세션 관리 (나중에 개선 가능)
    user_message: safeQuestion
  };
  
  console.log("requestData:", requestData);

  const response = await fetch(`${backendUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData),
  });
  const data = await response.json();
  return new Response(JSON.stringify({ answer: data.response }), {
    headers: { "Content-Type": "application/json" },
  });
}
