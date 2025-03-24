// C:\Users\katle\Desktop\theFlex\lastLast\app\appgen\src\app\api\suggest\route.ts
import { NextResponse } from 'next/server';
import { Ollama } from "ollama";
import { PRIMARY_MODEL, getFallbackModel, getModelTemperature } from '@/utils/models';

const client = new Ollama();

async function generateSuggestionWithFallback(messages: any[]) {
  try {
    console.log("Ollama Suggest: Calling client.chat with messages:", messages);
    const response = await client.chat({
      messages,
      model: PRIMARY_MODEL,
      temperature: getModelTemperature(PRIMARY_MODEL),
      max_tokens: 200,
      top_p: 1,
    });
    console.log("Ollama Suggest: Primary response:", response);
    return response;
  } catch (error) {
    console.error("Ollama Suggest: Primary model failed, trying fallback model. Error:", error);
    const fallbackResponse = await client.chat({
      messages,
      model: getFallbackModel(),
      temperature: getModelTemperature(getFallbackModel()),
      max_tokens: 2048,
      top_p: 1,
    });
    console.log("Ollama Suggest: Fallback response:", fallbackResponse);
    return fallbackResponse;
  }
}

export async function POST(request: Request) {
  try {
    const { html } = await request.json();

    if (!html) {
      return NextResponse.json(
        { error: 'HTML content is required' },
        { status: 400 }
      );
    }

    console.log("Ollama Suggest: Generating suggestion for HTML content:", html);
    const completion = await generateSuggestionWithFallback([
      {
        role: 'user',
        content: `Given this HTML content, suggest a concise title and brief description that captures the essence of the app. The title should be descriptive, while the description should explain what the app does in a single sentence. Format the response as JSON with "title" and "description" fields.

<app html>
${html}
</app html>`
      },
    ]);
    console.log("Ollama Suggest: Full response:", completion);

    const responseContent = completion.choices[0]?.message?.content || '';
    const startIndex = responseContent.indexOf('{');
    const endIndex = responseContent.lastIndexOf('}');

    if (startIndex === -1 || endIndex === -1) {
      throw new Error('Invalid JSON response from AI');
    }

    const jsonContent = responseContent.substring(startIndex, endIndex + 1);
    const suggestions = JSON.parse(jsonContent);
    console.log("Ollama Suggest: Parsed suggestions:", suggestions);

    return NextResponse.json(suggestions);
  } catch (error) {
    console.error('Ollama Suggest: Error generating suggestions:', error);
    return NextResponse.json(
      { error: 'Failed to generate suggestions' },
      { status: 500 }
    );
  }
}
