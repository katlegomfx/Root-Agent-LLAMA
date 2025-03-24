import type { NextApiRequest, NextApiResponse } from 'next';
import { Ollama } from 'ollama';

const ollama = new Ollama();

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method !== 'POST') {
    res.setHeader('Allow', ['POST']);
    return res.status(405).end(`Method ${req.method} Not Allowed`);
  }

  const { userInput } = req.body;
  if (!userInput) {
    return res.status(400).json({ error: 'Missing userInput' });
  }

  let responseContent = "";

  try {
    console.log("Ollama Generate: Received prompt:", userInput);
    console.log("Ollama Generate: Calling ollama.generate with parameters:", {
      model: "llama3.2",
      prompt: userInput,
      stream: true,
    });

    // Call Ollama's generate method with streaming enabled
    const stream = await ollama.generate({
      model: "llama3.2",
      prompt: userInput,
      stream: true
    });

    for await (const chunk of stream) {
      if (chunk.response) {
        responseContent += chunk.response;
      }
    }

    console.log("Ollama Generate: Received responseContent:", responseContent);
    res.status(200).json({ response: responseContent });
  } catch (error) {
    console.error("Ollama Generate: Error calling ollama.generate:", error);
    res.status(500).json({ error: 'Internal Server Error' });
  }
}
