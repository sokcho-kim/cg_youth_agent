const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatWelcome = document.getElementById('chat-welcome');

// 추천 태그 클릭 시 자동으로 질문 전송
if (chatWelcome) {
    chatWelcome.querySelectorAll('.chat-tag').forEach(tagBtn => {
        tagBtn.addEventListener('click', function() {
            const tagText = this.textContent.trim();
            const promptText = `${tagText}에 대해 알려줘`;
            sendMessage(promptText);
        });
    });
}

// 간단한 id(세션/유저) 생성 및 저장
function getUserId() {
    let id = localStorage.getItem('chatbot_user_id');
    if (!id) {
        id = 'user-' + Math.random().toString(36).substr(2, 12);
        localStorage.setItem('chatbot_user_id', id);
    }
    return id;
}

function addMessage(text, sender = 'user') {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message ' + sender;
    // 아바타
    if (sender === 'bot') {
        const avatar = document.createElement('div');
        avatar.className = 'chat-avatar bot';
        avatar.textContent = 'AI';
        messageDiv.appendChild(avatar);
    }
    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + sender;
    
    // 봇 메시지인 경우 마크다운을 HTML로 변환
    if (sender === 'bot') {
        bubble.innerHTML = convertMarkdownToHtml(text);
    } else {
        bubble.textContent = text;
    }
    
    messageDiv.appendChild(bubble);
    if (sender === 'user') {
        const avatar = document.createElement('div');
        avatar.className = 'avatar user';
        avatar.textContent = '나';
        messageDiv.appendChild(avatar);
    }
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// 마크다운을 HTML로 변환하는 함수
function convertMarkdownToHtml(markdown) {
    let html = markdown;
    
    // **텍스트** -> <strong>텍스트</strong>
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // *텍스트* -> <em>텍스트</em>
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // 줄바꿈을 <br>로 변환
    html = html.replace(/\n/g, '<br>');
    
    // 번호가 매겨진 목록 처리
    html = html.replace(/(\d+\.\s+)(.*?)(?=\d+\.\s+|$)/gs, function(match, number, content) {
        return `<div style="margin: 8px 0; padding-left: 20px;">${number}<span style="margin-left: 8px;">${content}</span></div>`;
    });
    
    // 제목 처리 (### 제목)
    html = html.replace(/###\s+(.*?)(?=\n|$)/g, '<h3 style="margin: 16px 0 8px 0; color: #333; font-size: 18px;">$1</h3>');
    
    // 제목 처리 (## 제목)
    html = html.replace(/##\s+(.*?)(?=\n|$)/g, '<h2 style="margin: 20px 0 12px 0; color: #333; font-size: 20px;">$1</h2>');
    
    // 제목 처리 (# 제목)
    html = html.replace(/^#\s+(.*?)(?=\n|$)/gm, '<h1 style="margin: 24px 0 16px 0; color: #333; font-size: 22px;">$1</h1>');
    
    return html;
}

function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-bubble';
    loadingDiv.textContent = '입력 중...';
    loadingDiv.id = 'loading-msg';
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

function removeLoading() {
    const loadingDiv = document.getElementById('loading-msg');
    if (loadingDiv) chatContainer.removeChild(loadingDiv);
}

async function sendMessage(message) {
    addMessage(message, 'user');
    userInput.value = '';
    sendBtn.disabled = true;
    removeWelcome();
    addLoading();
    try {
        const response = await fetch('https://youth-chatbot-backend.onrender.com/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: getUserId(), 
                user_message: message 
            })
        });
        const data = await response.json();
        removeLoading();
        // 응답이 answer 또는 response에 올 수 있으니 모두 처리
        addMessage(data.answer || data.response || '[오류] 답변이 없습니다.', 'bot');
    } catch (err) {
        removeLoading();
        addMessage('[오류] 서버와 통신할 수 없습니다.', 'bot');
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
}

function removeWelcome() {
    if (chatWelcome) {
        chatWelcome.style.display = 'none';
    }
}

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const message = userInput.value.trim();
    if (message) {
        sendMessage(message);
    }
});

userInput.addEventListener('input', function() {
    sendBtn.disabled = !userInput.value.trim();
});

// 입력창 비어있으면 버튼 비활성화
sendBtn.disabled = true; 