# test.py
import asyncio

from Bot.build.code.llm.llm_client import inference

output = inference([
    {
        'role': 'system',
        'content': 'You are an experienced AI scientist. You are working on a project to create a new language model. You have been given a dataset of text and your task is to create a language model that can generate new text based on the given dataset.'
    },
    {
        'role': 'user',
        'content': 'What is the best way to create a language model?'
    }
])


print(output)