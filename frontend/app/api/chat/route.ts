export const maxDuration = 30

export async function POST(req: Request) {
<<<<<<< HEAD
  try {
    const { messages } = await req.json();
    const lastMessage = messages[messages.length - 1];
    
    const response = await fetch("http://localhost:8000/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: "frontend-session",
        user_message: lastMessage.content
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Backend API error: ${response.status}`);
    }
    
    const data = await response.json();
    return new Response(JSON.stringify({ 
      id: Date.now().toString(),
      role: "assistant",
      content: data.response 
    }), {
      headers: { "Content-Type": "application/json" },
    });
  } catch (error) {
    console.error("API Error:", error);
    return new Response(JSON.stringify({ 
      id: Date.now().toString(),
      role: "assistant",
      content: "죄송합니다. 일시적으로 응답할 수 없습니다. 백엔드 서버를 확인해주세요." 
    }), {
      headers: { "Content-Type": "application/json" },
    });
  }
=======
  const { question } = await req.json();
  
  // 배포된 백엔드 URL로 고정
  const backendUrl = "https://youth-chatbot-backend.onrender.com";
  
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
>>>>>>> 8726ee43926763b1b1c6cb1eaa7475c462310a9a
}
