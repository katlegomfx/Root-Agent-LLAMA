// src/app/api/generate/route.ts

import { NextResponse } from "next/server";
import { Ollama } from "ollama";
import { constructPrompt } from "@/utils/prompt";
import {
	PRIMARY_MODEL,
	VANILLA_MODEL,
	PRIMARY_VISION_MODEL,
	FALLBACK_VISION_MODEL,
	getFallbackModel,
	getModelTemperature,
	getModelMaxTokens
} from "@/utils/models";
import {
	MAINTENANCE_GENERATION,
	MAINTENANCE_USE_VANILLA_MODEL,
} from "@/lib/settings";

const ollama = new Ollama();

async function tryCompletion(prompt: string, model: string, stream = false) {
	console.log("Ollama Completion: Calling client.chat with prompt:", prompt);
	console.log("Using model:", model, "stream:", stream);
	const completion = await ollama.chat({
		messages: [{ role: "user", content: prompt }],
		model: model,
		stream,
	});
	console.log("Ollama Completion: Received completion response:", completion);
	return completion;
}

async function generateWithFallback(prompt: string, model: string, stream = false) {
	try {
		console.log("Ollama Generate: Attempting primary call.");
		const chatCompletion = await tryCompletion(
			prompt,
			MAINTENANCE_USE_VANILLA_MODEL ? VANILLA_MODEL : model,
			stream
		);
		console.log("Ollama Generate: Primary call succeeded.");
		return chatCompletion;
	} catch (error) {
		console.error("Ollama Generate: Primary call failed. Error:", error);
		console.log("Ollama Generate: Attempting fallback call with model:", getFallbackModel());
		const fallbackCompletion = await tryCompletion(prompt, getFallbackModel(), stream);
		console.log("Ollama Generate: Fallback call succeeded. Response:", fallbackCompletion);
		return fallbackCompletion;
	}
}

async function getDrawingDescription(imageData: string): Promise<string> {
	try {
		console.log("Ollama Vision: Calling client.chat to describe drawing. Image data:", imageData);
		const chatCompletion = await ollama.chat({
			messages: [
				{
					role: "user",
					content: [
						{
							type: "text",
							text: "Describe this UI drawing in detail",
						},
						{
							type: "image_url",
							image_url: { url: imageData },
						},
					],
				},
			],
			model: PRIMARY_VISION_MODEL,
			stream: false
		});
		console.log("Ollama Vision: Received drawing description:", chatCompletion.message.content);
		return chatCompletion.message.content;
	} catch (error) {
		console.error("Ollama Vision: Primary vision call failed. Error:", error);
		console.log("Ollama Vision: Attempting fallback vision call.");
		const chatCompletion = await ollama.chat({
			messages: [
				{
					role: "user",
					content: [
						{
							type: "text",
							text: "Describe this UI drawing in detail",
						},
						{
							type: "image_url",
							image_url: { url: imageData },
						},
					],
				},
			],
			model: FALLBACK_VISION_MODEL,
			stream: false
		});
		console.log("Ollama Vision: Fallback vision call succeeded. Response:", chatCompletion.message.content);
		return chatCompletion.message.content;
	}
}

// Helper function to extract HTML from the response if wrapped in triple backticks.
function extractHtml(content: string): string {
	let html = content;
	if (html.includes("```html")) {
		const match = html.match(/```html\n([\s\S]*?)\n```/);
		html = match ? match[1] : html;
	}
	return html;
}

// Checks whether the string contains an HTML tag (case‑insensitive search for "<html")
function containsHtmlTag(content: string): boolean {
	return /<html\b/i.test(content);
}

export async function POST(request: Request) {
	if (MAINTENANCE_GENERATION) {
		return NextResponse.json(
			{ error: "We're currently undergoing maintenance. We'll be back soon!" },
			{ status: 500 }
		);
	}

	try {
		const { query, currentHtml, feedback, theme, drawingData, model, stream = false } =
			await request.json();
		let finalQuery = query;
		if (drawingData) {
			const drawingDescription = await getDrawingDescription(drawingData);
			finalQuery = `${query}\n\nDrawing description: ${drawingDescription}`;
		}

		const prompt = constructPrompt({
			...(finalQuery && { query: finalQuery }),
			currentHtml,
			currentFeedback: feedback,
			theme,
		});
		console.log("Ollama Generate Route: Constructed prompt:", prompt);

		// Streaming branch
		if (stream) {
			const encoder = new TextEncoder();
			console.log("Ollama Generate Route: Starting streaming generation.");
			const streamingCompletion = await generateWithFallback(prompt, model, true);

			const responseStream = new ReadableStream({
				async start(controller) {
					controller.enqueue(encoder.encode(JSON.stringify({ type: "start" }) + "\n"));
					try {
						let fullContent = "";
						for await (const chunk of streamingCompletion as any) {
							const content = chunk.delta?.content || "";
							if (content) {
								fullContent += content;
								console.log("Ollama Generate Route: Streaming chunk:", content);
								controller.enqueue(
									encoder.encode(
										JSON.stringify({ type: "chunk", content }) + "\n"
									)
								);
							}
						}
						// Extract HTML and retry if necessary
						let generatedHtml = extractHtml(fullContent);
						let retries = 0;
						while (!containsHtmlTag(generatedHtml) && retries < 3) {
							retries++;
							console.log(`Retry attempt ${retries} in streaming mode: No HTML tag found.`);
							// For retries, call non-streaming generation to get a fresh output
							const retryCompletion = await generateWithFallback(prompt, model, false) as any;
							generatedHtml = extractHtml(retryCompletion.message?.content || "");
						}
						console.log("Ollama Generate Route: Streaming complete. Final HTML:", generatedHtml);
						controller.enqueue(
							encoder.encode(
								JSON.stringify({
									type: "complete",
									html: generatedHtml,
									signature: generatedHtml,
								}) + "\n"
							)
						);
						controller.close();
					} catch (error) {
						console.error("Ollama Generate Route: Error in streaming:", error);
						controller.enqueue(
							encoder.encode(
								JSON.stringify({ type: "error", error: "Error generating content" }) + "\n"
							)
						);
						controller.close();
					}
				},
			});

			return new Response(responseStream, {
				headers: {
					"Content-Type": "text/event-stream",
					"Cache-Control": "no-cache",
					"Connection": "keep-alive",
				},
			});
		} else {
			// Non-streaming branch
			console.log("Ollama Generate Route: Starting non-streaming generation.");
			let attempt = 0;
			let generatedHtml = "";
			let usage = null;
			let chatCompletion;
			do {
				chatCompletion = await generateWithFallback(prompt, model, false) as any;
				generatedHtml = extractHtml(chatCompletion.message?.content || "");
				usage = chatCompletion.usage;
				attempt++;
				if (!containsHtmlTag(generatedHtml)) {
					console.log(`Retry attempt ${attempt} in non-streaming mode: No HTML tag found.`);
				}
			} while (!containsHtmlTag(generatedHtml) && attempt < 3);
			console.log("Ollama Generate Route: Non-streaming completion. Final HTML:", generatedHtml);
			return NextResponse.json({
				html: generatedHtml,
				signature: generatedHtml,
				usage: usage,
			});
		}
	} catch (error) {
		console.error("Ollama Generate Route: Error generating HTML:", error);
		return NextResponse.json({ error: "Failed to generate HTML" }, { status: 500 });
	}
}
