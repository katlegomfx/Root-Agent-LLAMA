// pages/index.tsx
"use client"
import { useState } from 'react';

export default function Home() {
  const [userInput, setUserInput] = useState('');
  const [conversation, setConversation] = useState<Array<{ role: string, content: string }>>([]);

  const handleChatSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim()) return;

    // Append the user message to the conversation for chat
    setConversation(prev => [...prev, { role: 'user', content: userInput }]);

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userInput })
      });
      const data = await res.json();
      setConversation(prev => [...prev, { role: 'assistant', content: data.response }]);
      setUserInput('');
    } catch (err) {
      console.error(err);
    }
  };

  const handleGenerate = async () => {
    if (!userInput.trim()) return;

    // Append the user message to the conversation for generate
    setConversation(prev => [...prev, { role: 'user', content: userInput }]);

    try {
      const res = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ userInput })
      });
      const data = await res.json();
      setConversation(prev => [...prev, { role: 'assistant', content: data.response }]);
      setUserInput('');
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div style={{ margin: '2rem' }}>
      <h1>Chat with Ollama</h1>
      <div style={{ marginBottom: '1rem', border: '1px solid #ccc', padding: '1rem', minHeight: '300px' }}>
        {conversation.map((msg, idx) => (
          <p key={idx}><strong>{msg.role}:</strong> {msg.content}</p>
        ))}
      </div>
      <form onSubmit={handleChatSubmit}>
        <input
          type="text"
          value={userInput}
          onChange={(e) => setUserInput(e.target.value)}
          placeholder="Type your message"
          style={{ width: '80%', marginRight: '1rem' }}
        />
        <button type="submit">Chat</button>
        <button type="button" onClick={handleGenerate} style={{ marginLeft: '0.5rem' }}>
          Generate
        </button>
      </form>
    </div>
  );
}
