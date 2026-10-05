const chatConversation = document.getElementById('chat-conversation');
const chatForm = document.querySelector('.chat-form');
const ragSearch = document.getElementById('rag-search');

const API_BASE_URL = (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:8000'           
  : 'https://finalyze-jfka.onrender.com';         

function createBubble(text, type) {
  const bubble = document.createElement('div');
  bubble.className = `chat-bubble ${type === 'user' ? 'user-bubble' : 'llm-bubble'}`;
  bubble.textContent = text;
  chatConversation.appendChild(bubble);
  chatConversation.scrollTop = chatConversation.scrollHeight;
}

chatForm.addEventListener('submit', async (event) => {
  event.preventDefault();

  const message = ragSearch.value.trim();
  if (!message) {
    return;
  }

  createBubble(message, 'user');
  ragSearch.value = '';

  const thinkingBubble = document.createElement('div');
  thinkingBubble.className = 'chat-bubble llm-bubble';
  thinkingBubble.textContent = 'Thinking...';
  chatConversation.appendChild(thinkingBubble);
  chatConversation.scrollTop = chatConversation.scrollHeight;

  try {
    const response = await fetch(`${API_BASE_URL}/chat/model`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });

    thinkingBubble.remove();

    if (response.status === 429) {
      createBubble('Rate limit exceeded. Please try again in a few minutes.', 'llm');
    } else if (!response.ok) {
      createBubble('Something went wrong generating a response. Please try again.', 'llm');
    } else {
      const data = await response.json();
      createBubble(data.response, 'llm');
    }
  } catch (error) {
    thinkingBubble.remove();
    createBubble('Unable to reach the chat backend.', 'llm');
  }
});
