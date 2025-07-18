const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');
const chatWelcome = document.getElementById('chat-welcome');
const policyList = document.getElementById('policy-list');
const policySidebar = document.getElementById('policy-sidebar');
 
 
 
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
        avatar.className = 'chat-avatar';
        avatar.textContent = 'AI';
        messageDiv.appendChild(avatar);
    }
   
    const bubble = document.createElement('div');
    bubble.className = 'bubble ' + sender;
   
    // 봇 메시지인 경우 마크다운을 HTML로 변환
    if (sender === 'bot') {
        bubble.innerHTML = parseMarkdown(text);
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
   
    // 스크롤을 부드럽게 맨 아래로 이동
    setTimeout(() => {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}
 
// 마크다운을 HTML로 변환하는 함수
function parseMarkdown(markdown) {
    let html = markdown;
 
    // 1. 제목 변환 (###, ##, #)
    html = html.replace(/###\s+(.*?)(?=\n|$)/g, '<div class="markdown-title-3">$1</div>');
    html = html.replace(/##\s+(.*?)(?=\n|$)/g, '<div class="markdown-title-2">$1</div>');
    html = html.replace(/^#\s+(.*?)(?=\n|$)/gm, '<div class="markdown-title-1">$1</div>');
 
    // 2. 굵게/기울임
    html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');
 
    // 3. 줄바꿈
    html = html.replace(/\n/g, '<br>');
 
    // 4. 번호가 매겨진 목록 (1. 2. 3. ...)
    html = html.replace(/(\d+\.\s+)(.*?)(?=\d+\.\s+|$)/gs, function(match, number, content) {
        return `<div style="margin: 8px 0; padding-left: 20px;">${number}<span style="margin-left: 8px;">${content}</span></div>`;
    });
 
    // 5. [자세히 보기] 링크 변환
    html = html.replace(/\[자세히 보기\]\s*(https?:\/\/[^\s<>]+)/g, '<a href="$1" target="_blank" style="color: #667eea; text-decoration: underline;">자세히 보기</a>');
 
    // 6. 일반 URL을 클릭 가능한 링크로 변환 (이미 HTML 링크가 아닌 경우)
    html = html.replace(/(?<!<a[^>]*>)(https?:\/\/[^\s<>]+)(?![^<]*<\/a>)/g, '<a href="$1" target="_blank" style="color: #667eea; text-decoration: underline;">$1</a>');
 
    return html;
}
 
function addLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'loading-bubble';
    loadingDiv.textContent = '입력 중...';
    loadingDiv.id = 'loading-msg';
    chatContainer.appendChild(loadingDiv);
   
    // 스크롤을 부드럽게 맨 아래로 이동
    setTimeout(() => {
        chatContainer.scrollTo({
            top: chatContainer.scrollHeight,
            behavior: 'smooth'
        });
    }, 100);
}
 
function removeLoading() {
    const loadingDiv = document.getElementById('loading-msg');
    if (loadingDiv) chatContainer.removeChild(loadingDiv);
}
 
// 정책 목록 표시 함수 (remaining_docs용)
function displayRemainingPolicies(policies) {
    policyList.innerHTML = '';
    if (!policies || policies.length === 0) {
        policySidebar.classList.remove('show');
        return;
    }
    policies.forEach(policy => {
        const policyDiv = document.createElement('div');
        policyDiv.className = 'policy-item';
        if (policy.title && policy.url) {
            policyDiv.innerHTML = `<a href="${policy.url}" target="_blank" rel="noopener noreferrer" style="color: #667eea; text-decoration: underline;">${policy.title}</a>`;
        } else if (policy.title) {
            policyDiv.textContent = policy.title;
        } else {
            policyDiv.textContent = "정책 정보";
        }
        policyList.appendChild(policyDiv);
    });
    policySidebar.classList.add('show');
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
       
        // 백엔드에서 remaining_docs가 있으면 오른쪽 사이드바에 표시
        if (data.remaining_docs && data.remaining_docs.length > 0) {
            displayRemainingPolicies(data.remaining_docs);
        } else {
            // remaining_docs가 없으면 사이드바를 숨김
            policySidebar.classList.remove('show');
        }
       
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