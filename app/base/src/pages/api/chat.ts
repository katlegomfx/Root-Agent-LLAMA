import type { NextApiRequest, NextApiResponse } from 'next';
import { Ollama } from 'ollama';

const ollama = new Ollama();

// In-memory conversation history (demo purposes)
const messages: Array<{ role: string, content: string }> = [];

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }
  
  const { userInput } = req.body;
  if (!userInput) {
    return res.status(400).json({ error: 'Missing userInput' });
  }

  console.log("Ollama Chat: Received userInput:", userInput);
  
  let responseContent = "";
  
  try {
    const chatMessages = [
      ...messages,
      { role: "system", content: "You are a helpful assistant. You only give a short sentence by answer." },
      { role: "user", content: userInput }
    ];
    console.log("Ollama Chat: Calling ollama.chat with parameters:", {
      model: "llama3.2",
      messages: chatMessages,
      stream: true,
    });
    
    // Call Ollama with streaming enabled
    const stream = await ollama.chat({
      model: "llama3.2",
      messages: chatMessages,
      stream: true,
    });
    
    for await (const chunk of stream) {
      if (chunk.message) {
        responseContent += chunk.message.content;
      }
    }
    
    console.log("Ollama Chat: Received responseContent:", responseContent);
    
    // Update conversation history
    messages.push(
      { role: "user", content: userInput },
      { role: "assistant", content: responseContent }
    );
    
    res.status(200).json({ response: responseContent });
  } catch (error) {
    console.error("Ollama Chat: Error calling ollama.chat:", error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
}
