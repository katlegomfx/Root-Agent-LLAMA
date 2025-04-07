# Bot\build\code\cli\next\utils\nextBuilder\backend\ai\ai_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_api_route  # nopep8

ROUTE_API_TEMPLATE = """import { fileURLToPath } from "url";
import path from "path";
import { LlamaModel, LlamaContext, LlamaChatSession } from "node-llama-cpp";

export default async function inference(req, res) {

    // console.log(req.body)
    try {
        const { messages } = req.body;

        const __dirname = path.dirname(fileURLToPath(import.meta.url));

        const model = new LlamaModel({
            modelPath: path.join(__dirname, './../../../public/tinyllama-1.1b-chat-v1.0.Q5_K_M.gguf'),
            // contextSize: 8192,
            contextSize: 8192/2,
            // batchSize: 8192
            batchSize: 8192/2
        });
        const context = new LlamaContext({ model });
        const session = new LlamaChatSession({ context });

        const q1 = messages;
        console.log(q1);

        const a1 = await session.prompt(q1);
        const processedResponse = a1.replace(/User: /g, '');

        console.log("AI: " + processedResponse);

        // { userMessage: q1, aiResponse: processedResponse }
        return res.status(200).json(
            {
                choices: [
                    {
                        message: {
                        content: processedResponse
                        }
                    }
                ]
            }
        );
    } catch (error) {
        console.error("An error occurred:", error);
        res.status(500).json({ error: "Internal Server Error" });
    }
}
"""

create_api_route('inference', ROUTE_API_TEMPLATE)
