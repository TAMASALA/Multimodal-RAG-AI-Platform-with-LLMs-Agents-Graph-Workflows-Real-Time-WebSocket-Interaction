import asyncio
from app.database.database import AsyncSessionLocal
from app.rag.retriever import retrieve

async def main():
    async with AsyncSessionLocal() as db:
        results = await retrieve(db, 'What projects does Vinay have?')
        print('count', len(results))
        for r in results:
            print(r.score, r.chunk.chunk_type.value, r.chunk.page_number, r.chunk.content[:200].replace('\n', ' '))

asyncio.run(main())
