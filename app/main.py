"""
FastAPI application entrypoint. Wires up CORS, lifespan startup/shutdown
(DB init, embedding model warm-up, FAISS index load), and mounts all routes.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes import api_router
from app.config import settings
from app.database.database import init_db
from app.embeddings.embedding_service import get_model
from app.embeddings.faiss_store import get_faiss_store
from app.utils.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.APP_NAME} in {settings.APP_ENV} mode...")
    settings.ensure_directories()

    await init_db()
    logger.info("Database initialized.")

    get_model()  # warm up embedding model at startup, not on first request
    store = get_faiss_store()
    logger.info(f"FAISS index ready with {store.ntotal} vectors.")

    yield

    logger.info("Shutting down. Persisting FAISS index...")
    get_faiss_store().save()


app = FastAPI(
    title="Multimodal RAG API",
    description="Production-ready Multimodal Retrieval-Augmented Generation system.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

# Serves extracted page/graph/figure images referenced by chunk.image_path so
# the frontend's ImageViewer/GraphViewer can render them directly by URL
# (e.g. GET /static/images/<filename>). Uploaded PDFs are intentionally NOT
# statically mounted; they're served through the authenticated-by-id
# /api/documents/{id}/file endpoint instead (see api/documents.py).
settings.ensure_directories()
app.mount("/static/images", StaticFiles(directory=settings.IMAGE_DIR), name="images")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host=settings.APP_HOST, port=settings.APP_PORT, reload=True)
    print("Groq Key:", settings.GROQ_API_KEY[:10] if settings.GROQ_API_KEY else "NOT FOUND")
