export const maxDuration = 30

export async function POST(req: Request) {
  const { question } = await req.json();
  const response = await fetch("http://localhost:8000/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const data = await response.json();
  return new Response(JSON.stringify({ answer: data.answer }), {
    headers: { "Content-Type": "application/json" },
  });
}
