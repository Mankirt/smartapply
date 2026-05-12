import logging
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import asyncpg

from app.config.database import get_db
from app.models.schemas import ResumeResponse, ResumeSection
from app.services.parser import parse_pdf_to_sections
from app.services.embeddings import generate_embeddings_batch

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/upload", response_model=ResumeResponse)
async def upload_resume(
    file: UploadFile = File(...),
    db: asyncpg.Connection = Depends(get_db),
):
    logger.info(f"Resume upload started: {file.filename}")

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    pdf_bytes = await file.read()
    if len(pdf_bytes) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    # Step 1 — parse PDF into sections
    try:
        sections = await parse_pdf_to_sections(pdf_bytes)
    except Exception as e:
        logger.error(f"PDF parsing failed: {e}")
        raise HTTPException(status_code=422, detail=f"Could not parse PDF: {str(e)}")

    # store resume record
    row = await db.fetchrow(
    "INSERT INTO resumes (filename, raw_content) VALUES ($1, $2) RETURNING id, created_at",
    file.filename,
    " ".join(s.content for s in sections),
    )
    resume_id = row["id"]
    created_at = row["created_at"]

    # Step 2 — generate embeddings for ALL sections in one batch call
    contents = [s.content for s in sections]
    embeddings = generate_embeddings_batch(contents)

    # store each section with its embedding
    for section, embedding in zip(sections, embeddings):
        await db.execute(
            """
            INSERT INTO resume_sections
                (resume_id, section_type, title, content, order_index, embedding)
            VALUES ($1, $2, $3, $4, $5, $6)
            """,
            resume_id,
            section.section_type,
            section.title,
            section.content,
            section.order,
            str(embedding),
        )

    logger.info(f"Resume stored: id={resume_id}, sections={len(sections)}")

    return ResumeResponse(
        id=resume_id,
        filename=file.filename,
        sections=sections,
        created_at=created_at,
    )


@router.get("/{resume_id}", response_model=ResumeResponse)
async def get_resume(
    resume_id: int,
    db: asyncpg.Connection = Depends(get_db),
):
    resume = await db.fetchrow(
        "SELECT * FROM resumes WHERE id = $1", resume_id
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    rows = await db.fetch(
        "SELECT * FROM resume_sections WHERE resume_id = $1 ORDER BY order_index",
        resume_id,
    )
    sections = [
        ResumeSection(
            section_type=r["section_type"],
            title=r["title"],
            content=r["content"],
            order=r["order_index"],
        )
        for r in rows
    ]

    return ResumeResponse(
        id=resume["id"],
        filename=resume["filename"],
        sections=sections,
        created_at=resume["created_at"],
    )