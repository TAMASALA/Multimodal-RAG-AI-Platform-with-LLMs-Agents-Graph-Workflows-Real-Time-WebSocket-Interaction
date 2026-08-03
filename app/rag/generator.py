"""
Generates the final answer text from a built prompt, in both blocking and
streaming modes.
"""
from typing import AsyncIterator

from app.llm.groq_client import chat_completion, chat_completion_stream
from app.llm.prompts import RAG_SYSTEM_PROMPT


async def generate_answer(user_prompt: str) -> str:
    return await chat_completion(system_prompt=RAG_SYSTEM_PROMPT, user_prompt=user_prompt)


async def generate_answer_stream(user_prompt: str) -> AsyncIterator[str]:
    async for token in chat_completion_stream(
        system_prompt=RAG_SYSTEM_PROMPT, user_prompt=user_prompt
    ):
        yield token

from typing import AsyncIterator
from app.llm.groq_client import chat_completion_stream
from app.llm.prompts import RAG_SYSTEM_PROMPT

async def generate_answer_stream(user_prompt: str) -> AsyncIterator[str]:
    print("Starting stream")

    async for token in chat_completion_stream(
        system_prompt=RAG_SYSTEM_PROMPT,
        user_prompt=user_prompt,
    ):
        print("TOKEN:", repr(token))
        yield token

    print("Finished stream")