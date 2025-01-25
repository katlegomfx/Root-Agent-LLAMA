# makeFlaskTest.py
import asyncio
import requests

from Bot.build.code.llm.llm_client import process_user_messages_with_model

# Base URL of the Flask app
BASE_URL = 'http://127.0.0.1:5000'



def post_echo(message):
    url = f"{BASE_URL}/special"
    payload = {"message": message}
    try:

        # input('continue')

        response = requests.post(url, json=payload)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error during POST request to {url}: {e}")


if __name__ == '__main__':

    runs = 0
    tries = 5
    base_prompt = [{'role': 'system', 'content': '''You need to build the most Amazing Application that will make money in NextJS and mysql to keep the comapany going. You work at FlexData and will be using the internal AI system to do tasks. Start your message with:
        - tool <request>: Use a internal tools.
        - self <request>: ask about internal code.
'''}, {
        'role': 'user', 'content': 'Please work with internal AI system to build the application'}]

    while runs < tries:

        async def handle_request(messages):
            response = await process_user_messages_with_model(messages)
            return response
        
        base_response = asyncio.run(handle_request(base_prompt))


        base_prompt.append({'role': 'user', 'content': base_response})

        tool_response = post_echo(base_response)

        try:
            base_prompt.append({'role': 'assistant', 'content': tool_response['response']})
            runs += 1
        except Exception as e:
            print(e)
