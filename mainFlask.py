import os
import json
from datetime import datetime
import json
import asyncio

from flask import Flask, request, jsonify
from flask_cors import CORS, cross_origin

from Bot.build.code.llm.prompts import get_message_context_summary, process_user_messages_with_model, load_message_template
from Bot.build.code.cli.cli_application import CLIApplication
from Bot.build.code.session.constants import (
    summary_prefix,
    ai_summaries_path,
    gen_ai_path
)

app = Flask(__name__)
CORS(app)

# File to persist context
CONTEXT_FILE = 'flaskContextSession1.md'


def load_context():
    """Load the conversation context from a markdown file. 
       If the file does not exist, return an empty list.
    """
    if os.path.exists(CONTEXT_FILE):
        with open(CONTEXT_FILE, 'r') as f:
            try:
                data = json.load(f)
                print("Context loaded:", data)
                return data
            except Exception as e:
                print("Error loading context, initializing empty context. Error:", e)
                return []
    else:
        # Create an empty file
        with open(CONTEXT_FILE, 'w') as f:
            json.dump([], f)
        return []


def save_context(context):
    """Save the conversation context to a markdown file."""
    with open(CONTEXT_FILE, 'w') as f:
        json.dump(context, f, indent=4)


# Initialize global context by loading from file.




async def trim_context(messages_context, max_length: int = 28):
    """Trim the chat context to the last `max_length` interactions.
       If the context is too long, create a summary and prepend it.
    """
    if len(messages_context) > max_length:
        # Get a summary of the existing context.
        summary = await get_message_context_summary(messages_context)
        # Create a new context that starts with the summary followed by the last max_length messages.
        new_context = [{'role': 'user', 'content': summary}] + \
            messages_context[-max_length:]
        return new_context
    return messages_context


@app.route('/special', methods=['POST'])
@cross_origin()
def case1():
    data = request.get_json()

    async def handle_request():
        # Create a prompt with the current context.
        context = load_context()
        prompt = load_message_template('base', context)
        prompt.append({'role': 'user', 'content': data['message']})

        response = await process_user_messages_with_model(prompt)
        prompt.append({'role': 'assistant', 'content': response})

        # Update the global context with the new messages.
        # Declare global to update the module-level variable.
        

        context.append({'role': 'user', 'content': data['message']})
        context.append({'role': 'assistant', 'content': response})

        # Trim the context if it grows beyond the max length.
        context = await trim_context(context)

        # Save the updated context to file.
        save_context(context)

        return {'response': response}

    # Run the async function and get the result
    result = asyncio.run(handle_request())
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
