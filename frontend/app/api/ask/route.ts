export async function POST(req: Request) {
  const { prompt } = await req.json();

  // 백엔드 /ask API로 요청
  const response = await fetch("https://youth-chatbot-backend.onrender.com/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });

  const data = await response.json();
  return new Response(JSON.stringify({ answer: data.response }), {
    headers: { "Content-Type": "application/json" },
  });
} 