import asyncio
from app.database.database import AsyncSessionLocal
from app.database.crud import get_chunks_for_document

async def main():
    doc_id = '921abdf04ce34802a08848c24f9f44d0'
    async with AsyncSessionLocal() as db:
        chunks = await get_chunks_for_document(db, doc_id)
        print('chunks', len(chunks))
        for c in chunks[:10]:
            print('---', c.chunk_type, 'page', c.page_number)
            print(c.content[:500])

asyncio.run(main())
