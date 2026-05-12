import logging
import time
import json
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
import asyncpg

from app.config.database import get_db
from app.config.settings import get_settings
from app.models.schemas import AnalyzeRequest, AnalysisResponse
from app.services.similarity import find_similar_sections
from app.services.analyzer import run_analysis_pipeline, stream_analysis

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# simple in-memory rate limiter — {ip: [timestamp, timestamp, ...]}
_rate_limit_store: dict[str, list[float]] = defaultdict(list)


def check_rate_limit(client_ip: str):
    now = time.time()
    window = settings.analyze_rate_limit_window
    limit = settings.analyze_rate_limit

    # remove timestamps outside the current window
    _rate_limit_store[client_ip] = [
        t for t in _rate_limit_store[client_ip]
        if now - t < window
    ]

    if len(_rate_limit_store[client_ip]) >= limit:
        logger.warning(f"Rate limit exceeded for IP: {client_ip}")
        raise HTTPException(
            status_code=429,
            detail=f"Rate limit exceeded. Max {limit} requests per {window}s."
        )

    _rate_limit_store[client_ip].append(now)


@router.post("/", response_model=AnalysisResponse)
async def analyze(
    request: Request,
    payload: AnalyzeRequest,
    db: asyncpg.Connection = Depends(get_db),
):
    client_ip = request.client.host
    check_rate_limit(client_ip)

    logger.info(f"Analysis started: resume_id={payload.resume_id}")

    # verify resume exists
    resume = await db.fetchrow(
        "SELECT * FROM resumes WHERE id = $1", payload.resume_id
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # fetch all resume sections
    section_rows = await db.fetch(
        "SELECT * FROM resume_sections WHERE resume_id = $1 ORDER BY order_index",
        payload.resume_id,
    )
    if not section_rows:
        raise HTTPException(status_code=422, detail="Resume has no parsed sections")

    # Step 3 — find similar sections via pgvector
    similar_sections = await find_similar_sections(
        jd_text=payload.jd_text,
        resume_id=payload.resume_id,
        db=db,
    )

    # Steps 4 + 5 — Claude analyzes fit and suggests improvements
    analysis = await run_analysis_pipeline(
        resume_text=resume["raw_content"],
        jd_text=payload.jd_text,
        sections=section_rows,
        similar_sections=similar_sections,
    )

    # persist analysis
    row = await db.fetchrow(
        """
        INSERT INTO analyses
            (resume_id, jd_text, fit_score, matching_skills, missing_keywords, summary)
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, created_at
        """,
        payload.resume_id,
        payload.jd_text,
        analysis["fit_score"],
        json.dumps(analysis["matching_skills"]),
        json.dumps(analysis["missing_keywords"]),
        analysis["summary"],
    )

    logger.info(f"Analysis complete: id={row['id']}, score={analysis['fit_score']}")

    return AnalysisResponse(
        id=row["id"],
        resume_id=payload.resume_id,
        fit_score=analysis["fit_score"],
        matching_skills=analysis["matching_skills"],
        missing_keywords=analysis["missing_keywords"],
        summary=analysis["summary"],
        sections=analysis["sections"],
        created_at=row["created_at"],
    )


@router.post("/stream")
async def analyze_stream(
    request: Request,
    payload: AnalyzeRequest,
    db: asyncpg.Connection = Depends(get_db),
):
    client_ip = request.client.host
    check_rate_limit(client_ip)

    resume = await db.fetchrow(
        "SELECT * FROM resumes WHERE id = $1", payload.resume_id
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    similar_sections = await find_similar_sections(
        jd_text=payload.jd_text,
        resume_id=payload.resume_id,
        db=db,
    )

    return StreamingResponse(
        stream_analysis(
            jd_text=payload.jd_text,
            similar_sections=similar_sections,
        ),
        media_type="text/event-stream",
    )