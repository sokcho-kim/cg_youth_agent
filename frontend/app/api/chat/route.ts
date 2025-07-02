export const maxDuration = 30

export async function POST(req: Request) {
  const { question } = await req.json();
  
  // 환경변수에서 백엔드 URL 가져오기 (배포 시 설정)
  const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  
  // 백엔드 API 형식에 맞게 요청 데이터 구성
  const requestData = {
    session_id: "default_session", // 세션 관리 (나중에 개선 가능)
    user_message: question
  };
  
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
