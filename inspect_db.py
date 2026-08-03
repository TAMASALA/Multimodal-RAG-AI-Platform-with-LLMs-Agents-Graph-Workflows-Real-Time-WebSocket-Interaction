import asyncio
from app.database.database import AsyncSessionLocal
from app.database.crud import list_documents

async def main():
    async with AsyncSessionLocal() as db:
        docs = await list_documents(db)
        print('documents', len(docs))
        for doc in docs:
            print(doc.id, doc.filename, doc.status.value, doc.num_pages)

asyncio.run(main())
