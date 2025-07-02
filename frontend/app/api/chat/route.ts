export const maxDuration = 30

export async function POST(req: Request) {
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
}
