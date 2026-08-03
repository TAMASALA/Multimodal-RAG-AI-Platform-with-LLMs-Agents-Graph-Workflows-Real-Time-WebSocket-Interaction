"""
End-to-end ingestion pipeline for a single uploaded PDF document.

Flow per page:
  1. Extract raw text (PyMuPDF).
  2. If text is sparse -> render page image and run OCR fallback.
  3. Extract tables (pdfplumber) -> serialize to markdown chunks.
  4. Extract embedded images -> OCR each; if it looks like a chart/graph,
     additionally caption it with the vision LLM.
  5. Detect candidate equations in the page text -> reconstruct via LLM.
  6. Chunk all text-bearing content, embed, add to FAISS, persist Chunk rows.

The pipeline is designed to run as a FastAPI BackgroundTask after upload,
so it manages its own DB session rather than depending on a request-scoped one.
"""
from app.config import settings
from app.database.crud import (
    create_chunk,
    update_document_pages,
    update_document_status,
)
from app.database.database import AsyncSessionLocal
from app.database.models import DocumentStatus, ChunkType
from app.embeddings.embedding_service import embed_texts
from app.embeddings.faiss_store import get_faiss_store
from app.ingestion.chunking import split_text
from app.ingestion.metadata import build_chunk_metadata
from app.ingestion.pdf_parser import get_page_count, iter_pages, is_page_text_sparse
from app.processing.equations import extract_candidate_equations, reconstruct_equation
from app.processing.graphs import describe_graph_image, looks_like_graph
from app.processing.images import extract_page_images, render_page_as_image
from app.processing.ocr import extract_text_from_image, has_meaningful_text
from app.processing.tables import extract_tables_from_page
from app.utils.helpers import timed
from app.utils.logger import logger
from PIL import Image


async def _persist_chunk(
    db,
    document_id: str,
    document_name: str,
    content: str,
    chunk_type: str,
    page_number: int,
    image_path: str | None = None,
    extra_meta: dict | None = None,
) -> None:
    """Embeds a single piece of content, adds it to FAISS, and stores the Chunk row.
    Kept small so both text and multimodal chunks flow through one code path."""
    if not content or not content.strip():
        return

    vectors = embed_texts([content])
    store = get_faiss_store()
    start, _ = store.add(vectors)

    meta = build_chunk_metadata(
        document_id=document_id,
        document_name=document_name,
        page_number=page_number,
        chunk_type=chunk_type,
        extra=extra_meta,
    )

    await create_chunk(
        db,
        document_id=document_id,
        chunk_type=chunk_type,
        content=content,
        page_number=page_number,
        faiss_index=start,
        image_path=image_path,
        meta=meta,
    )


async def process_document(document_id: str, file_path: str, filename: str) -> None:
    """Main entry point invoked as a background task after upload."""
    async with AsyncSessionLocal() as db:
        try:
            await update_document_status(db, document_id, DocumentStatus.PROCESSING)

            with timed(f"ingest:{filename}"):
                num_pages = get_page_count(file_path)
                await update_document_pages(db, document_id, num_pages)

                for page_index, page_text in iter_pages(file_path):
                    page_number = page_index + 1

                    # --- 1. Plain text (with OCR fallback for sparse/scanned pages) ---
                    text_for_chunks = page_text
                    if is_page_text_sparse(page_text):
                        logger.info(
                            f"Page {page_number} of {filename} looks scanned; running OCR fallback."
                        )
                        full_page_img = render_page_as_image(
                            file_path, page_index, settings.IMAGE_DIR
                        )
                        ocr_text = extract_text_from_image(full_page_img)
                        if has_meaningful_text(ocr_text):
                            text_for_chunks = ocr_text
                            for chunk in split_text(ocr_text):
                                await _persist_chunk(
                                    db, document_id, filename, chunk, ChunkType.OCR.value,
                                    page_number, image_path=full_page_img,
                                )
                    else:
                        for chunk in split_text(page_text):
                            await _persist_chunk(
                                db, document_id, filename, chunk, ChunkType.TEXT.value, page_number
                            )

                    # --- 2. Tables ---
                    for table_md in extract_tables_from_page(file_path, page_index):
                        await _persist_chunk(
                            db, document_id, filename, table_md, ChunkType.TABLE.value, page_number
                        )

                    # --- 3. Embedded images: OCR + optional graph captioning ---
                    image_paths = extract_page_images(file_path, page_index, settings.IMAGE_DIR)
                    for img_path in image_paths:
                        ocr_text = extract_text_from_image(img_path)
                        try:
                            with Image.open(img_path) as im:
                                width, height = im.size
                        except Exception:
                            width, height = (0, 0)

                        if looks_like_graph(width, height, ocr_text):
                            description = await describe_graph_image(img_path)
                            content = description or ocr_text
                            chunk_type = ChunkType.GRAPH.value
                        else:
                            content = ocr_text
                            chunk_type = ChunkType.IMAGE.value

                        if has_meaningful_text(content, min_chars=5):
                            await _persist_chunk(
                                db, document_id, filename, content, chunk_type,
                                page_number, image_path=img_path,
                            )

                    # --- 4. Equations ---
                    for candidate in extract_candidate_equations(text_for_chunks):
                        reconstructed = await reconstruct_equation(candidate)
                        await _persist_chunk(
                            db, document_id, filename, reconstructed, ChunkType.EQUATION.value,
                            page_number, extra_meta={"raw_ocr": candidate},
                        )

                get_faiss_store().save()

            await update_document_status(db, document_id, DocumentStatus.READY)
            logger.info(f"Document '{filename}' ({document_id}) ingestion complete.")

        except Exception as exc:
            logger.exception(f"Ingestion failed for document {document_id}: {exc}")
            await update_document_status(db, document_id, DocumentStatus.FAILED, str(exc))
