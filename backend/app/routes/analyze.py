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

    logger.info(f"Analysis started: resume_id={payload.resume_id}, company={payload.company_name}")

    # verify resume exists
    resume = await db.fetchrow(
        "SELECT * FROM resumes WHERE id = $1", payload.resume_id
    )
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # fetch resume sections
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

    # persist analysis with company + role + filename
    row = await db.fetchrow(
        """
        INSERT INTO analyses
            (resume_id, jd_text, fit_score, matching_skills,
             missing_keywords, summary, company_name, role, resume_filename)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING id, created_at
        """,
        payload.resume_id,
        payload.jd_text,
        analysis["fit_score"],
        json.dumps(analysis["matching_skills"]),
        json.dumps(analysis["missing_keywords"]),
        analysis["summary"],
        payload.company_name,
        payload.role,
        resume["filename"],
    )

    analysis_id = row["id"]

    # save all suggestions to DB
    for section in analysis["sections"]:
        for suggestion in section["suggestions"]:
            # guard — skip if suggestion is not a dict
            if not isinstance(suggestion, dict):
                continue
            if not all(k in suggestion for k in ("original", "improved", "reason")):
                continue
                
            await db.execute(
                """
                INSERT INTO section_suggestions
                    (analysis_id, section_type, section_title,
                     similarity_score, original, improved, reason)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                """,
                analysis_id,
                section["section_type"],
                section["section_title"],
                section["similarity_score"],
                suggestion["original"],
                suggestion["improved"],
                suggestion["reason"],
            )

    # fetch suggestions back with their DB ids
    suggestion_rows = await db.fetch(
        """
        SELECT * FROM section_suggestions
        WHERE analysis_id = $1
        ORDER BY section_type, id
        """,
        analysis_id,
    )

    # rebuild sections with real DB ids
    sections_with_ids = {}
    for s in suggestion_rows:
        key = s["section_type"]
        if key not in sections_with_ids:
            sections_with_ids[key] = {
                "section_type": s["section_type"],
                "section_title": s["section_title"],
                "similarity_score": s["similarity_score"],
                "suggestions": [],
                "status": "pending",
            }
        sections_with_ids[key]["suggestions"].append({
            "id": s["id"],
            "original": s["original"],
            "improved": s["improved"],
            "reason": s["reason"],
            "status": "pending",
            "edited_content": None,
        })

    logger.info(f"Analysis complete: id={analysis_id}, score={analysis['fit_score']}")

    return AnalysisResponse(
        id=analysis_id,
        resume_id=payload.resume_id,
        fit_score=analysis["fit_score"],
        matching_skills=analysis["matching_skills"],
        missing_keywords=analysis["missing_keywords"],
        summary=analysis["summary"],
        sections=list(sections_with_ids.values()),
        company_name=payload.company_name,
        role=payload.role,
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