// export const maxDuration = 30

// export async function POST(req: Request) {
//   const body = await req.json();
//   let user_message = "";

//   if (body.messages && Array.isArray(body.messages)) {
//     // 모든 메시지 content를 줄바꿈으로 합침
//     user_message = (body.messages as Array<{ content: string }>).map((m) => m.content).join("\n");
//     console.log("messages merged user_message:", user_message);
//   } else if (typeof body.question === "string") {
//     user_message = body.question;
//   } else {
//     console.error("[Error] No valid user message found in request body.");
//   }

//   // 타입 및 값 확인
//   console.log("user_message type:", typeof user_message, "value:", user_message);

//   // fallback: string이 아니면 빈 문자열로 대체
//   if (typeof user_message !== "string") {
//     console.error("[Error] user_message must be a string. Fallback to empty string.");
//     user_message = "";
//   }

//   const backendUrl = "https://youth-chatbot-backend.onrender.com";
//   const requestData = {
//     session_id: "default_session",
//     user_message
//   };

//   console.log("requestData:", requestData);

//   const response = await fetch(`${backendUrl}/chat`, {
//     method: "POST",
//     headers: { "Content-Type": "application/json" },
//     body: JSON.stringify(requestData),
//   });
//   const data = await response.json();
//   return new Response(JSON.stringify({ answer: data.response }), {
//     headers: { "Content-Type": "application/json" },
//   });
// }

export const maxDuration = 30
 
export async function POST(req: Request) {
  const { messages } = await req.json();
  const lastMessage = messages[messages.length - 1];
  
  console.log("Frontend request - messages:", messages);
  console.log("Frontend request - lastMessage:", lastMessage);
  
  const backendUrl = "https://youth-chatbot-backend.onrender.com";
  const requestData = {
    session_id: "default_session",
    user_message: lastMessage.content
  };
 
  console.log("Backend request data:", requestData);
 
  const response = await fetch(`${backendUrl}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(requestData),
  });
  const data = await response.json();
  
  console.log("Backend response data:", data);
  console.log("Sending response to frontend:", data.response);
  
  // useChat 훅이 기대하는 messages 배열 형태로 응답
  return new Response(
    JSON.stringify({
      messages: [
        {
          id: Date.now().toString(),
          role: "assistant",
          content: data.response
        }
      ]
    }),
    {
      headers: { "Content-Type": "application/json" }
    }
  );
}
