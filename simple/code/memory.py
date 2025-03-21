import ast
import logging
import requests
from tqdm import tqdm
import chromadb
import json
from simple.code.inference import run_inference
from simple.code.logging_config import setup_logging

# Centralized logging setup
setup_logging()
chroma_client = chromadb.Client()


def get_or_create_collection(collection='conversations'):
    return chroma_client.get_or_create_collection(name=collection)


def embedText(writtenText, model='nomic-embed-text'):
    payload = {
        "model": model,
        "prompt": writtenText,
        "stream": True,
        "temperature": 0,
        "stop": "<|eot_id|>"
    }
    try:
        request_response = requests.post(
            "http://localhost:11434/api/embeddings",
            headers={"Content-Type": "application/json"},
            data=json.dumps(payload),
            stream=True,
            timeout=1000  # Added timeout for network requests
        )
        decoded_list = None
        for line in request_response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                decoded_dict = json.loads(decoded_line)
                decoded_list = decoded_dict['embedding']
        return decoded_list
    except Exception as e:
        logging.error(f"Error generating embedding: {e}")
        return None


def classify_embedding(query, context):
    classify_msg = (
        'You are an embedding classification AI agent. Your input will be a prompt and one embedded chunk of text. '
        'You will not respond as an AI assistant. You only respond "yes" or "no". '
        'Determine whether the context directly relates to the search query. '
        'If the context matches the search query requirements, respond "yes"; otherwise, respond "no".'
    )
    classify_convo = [
        {'role': 'system', 'content': classify_msg},
        {'role': 'user', 'content': 'SEARCH QUERY: What is the users name? \n\nEMBEDDED CONTEXT: You are Ai Flexi. How can I help you today?'},
        {'role': 'assistant', 'content': 'yes'},
        {'role': 'user', 'content': 'SEARCH QUERY: Llama3 Python Voice Assistant \n\nEMBEDDED CONTEXT: Siri is a voice assistant on Apple iOS and Mac OS.'},
        {'role': 'assistant', 'content': 'no'},
        {'role': 'user', 'content': f'SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context} '}
    ]
    classify_convo.append(
        {'role': "user", 'content': f'SEARCH QUERY: {query} \n\nEMBEDDED CONTEXT: {context} '})
    response = run_inference(classify_convo, None, None, "llama3.2")
    return response.strip().strip().lower()


def retrieve_embeddings(queries, db='conversations', n_results=2):
    embeddings = set()
    for query in tqdm(queries, desc='Retrieving Embeddings'):
        response = embedText(query)
        vector_db = get_or_create_collection(db)
        results = vector_db.query(
            query_embeddings=[response], n_results=n_results)
        best_embeddings = results[0]
        for best in best_embeddings:
            if best not in embeddings:
                if 'yes' in classify_embedding(query, best):
                    embeddings.add(best)
    return embeddings


def create_queries(prompt):
    query_message = (
        'You are a first principle reasoning search query AI agent. '
        'Generate a Python list of queries to search an embedding database for data needed to respond to the prompt. '
        'Return only a syntactically correct Python list.'
    )
    query_convo = [
        {'role': 'system', 'content': query_message},
        {'role': 'user', 'content': 'Write an email to my car insurance company and request lower rates.'},
        {'role': 'assistant',
            'content': '["What is the user\'s name?", "Who is the current auto insurer?", "What is the current monthly rate?"]'},
        {'role': 'user', 'content': 'How can I convert the speak function in my llama3 python voice assistant to use pyttsx3 instead?'},
        {'role': 'assistant',
            'content': '["Llama3 voice assistant", "Python voice assistant", "OpenAI TTS", "openai speak"]'},
    ]
    query_convo.append({'role': "user", 'content': prompt})
    response = run_inference(query_convo, None, None, "llama3.2")
    try:
        return ast.literal_eval(response)
    except Exception as e:
        logging.error(f"Error parsing queries: {e}")
        return [prompt]


def create_vector_db(conversations, vector_db_name='conversations'):
    vector_db_name = 'conversations'
    try:
        chroma_client.delete_collection(name=vector_db_name)
    except ValueError:
        pass
    vector_db = chroma_client.create_collection(name=vector_db_name)
    for c in conversations:
        serialized_convo = f'prompt: {c["prompt"]} response: {c["response"]}'
        embeddedTextResult = embedText(serialized_convo)
        vector_db.add(ids=[f"{c['id']}"], embeddings=[
                      embeddedTextResult], documents=[serialized_convo])


def example_usage(user_input):
    queries = create_queries(user_input)
    embeddings = retrieve_embeddings(queries)
    prompt = f'MEMORIES: {embeddings}\n\nUSER PROMPT: {user_input}'
    response = run_inference(
        [{'role': "user", 'content': prompt}], None, None, "llama3.2")
    return True


def add_response_to_db(response: str, response_id: str, vector_db_name: str = 'conversations'):
    """
    Adds the AI's valid response to the chromadb vector database.

    Args:
        response (str): The AI's valid response text.
        response_id (str): A unique identifier for this response.
        vector_db_name (str): The name of the vector DB collection.
    """
    collection = get_or_create_collection(vector_db_name)
    embedding = embedText(response)
    if not embedding:
        logging.error("Failed to generate embedding for the response.")
        return
    try:
        collection.add(ids=[response_id], embeddings=[
                       embedding], documents=[response])
        logging.info(
            f"Successfully added response {response_id} to the vector db '{vector_db_name}'.")
    except Exception as e:
        logging.error(f"Error adding response to vector db: {e}")
