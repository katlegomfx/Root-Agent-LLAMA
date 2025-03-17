import os
import asyncio
from browser_use import Agent
from langchain_ollama import ChatOllama

async def run_search() -> str:
    agent = Agent(
        task="Compare the price of gpt-4o and DeepSeek-V3",
        llm=ChatOllama(
            model="llama3.2-vision",
        )
    )

    result = await agent.run()
    return result


async def main():
    result = await run_search()
    print("\n\n", result)


if __name__ == "__main__":
    asyncio.run(main())
