import logging
from fastapi import APIRouter, Depends, HTTPException
import asyncpg
import json

from app.config.database import get_db
from app.models.schemas import AnalysisSummary, SectionReviewUpdate, AnalysisResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[AnalysisSummary])
async def list_analyses(
    resume_id: int | None = None,
    db: asyncpg.Connection = Depends(get_db),
):
    if resume_id:
        rows = await db.fetch(
            "SELECT * FROM analyses WHERE resume_id = $1 ORDER BY created_at DESC",
            resume_id,
        )
    else:
        rows = await db.fetch(
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT 50"
        )

    return [
        AnalysisSummary(
            id=r["id"],
            resume_id=r["resume_id"],
            fit_score=r["fit_score"],
            summary=r["summary"],
            company_name=r["company_name"],
            role=r["role"],
            resume_filename=r["resume_filename"],
            created_at=r["created_at"],
        )
        for r in rows
    ]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis(
    analysis_id: int,
    db: asyncpg.Connection = Depends(get_db),
):
    analysis = await db.fetchrow(
        "SELECT * FROM analyses WHERE id = $1", analysis_id
    )
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    # load suggestions with their saved reviews joined in
    suggestion_rows = await db.fetch(
        """
        SELECT
            s.id,
            s.section_type,
            s.section_title,
            s.similarity_score,
            s.original,
            s.improved,
            s.reason,
            r.status   AS review_status,
            r.edited_content AS review_edited
        FROM section_suggestions s
        LEFT JOIN section_reviews r
            ON r.suggestion_id = s.id
            AND r.analysis_id = $1
        WHERE s.analysis_id = $1
        ORDER BY s.section_type, s.id
        """,
        analysis_id,
    )

    # group by section
    sections_map = {}
    for s in suggestion_rows:
        key = s["section_type"]
        if key not in sections_map:
            sections_map[key] = {
                "section_type": s["section_type"],
                "section_title": s["section_title"],
                "similarity_score": s["similarity_score"],
                "suggestions": [],
                "status": "pending",
            }
        sections_map[key]["suggestions"].append({
            "id": s["id"],
            "original": s["original"],
            "improved": s["improved"],
            "reason": s["reason"],
            "status": s["review_status"] or "pending",
            "edited_content": s["review_edited"],
        })

    return AnalysisResponse(
        id=analysis["id"],
        resume_id=analysis["resume_id"],
        fit_score=analysis["fit_score"],
        matching_skills=json.loads(analysis["matching_skills"]),
        missing_keywords=json.loads(analysis["missing_keywords"]),
        summary=analysis["summary"],
        sections=list(sections_map.values()),
        company_name=analysis["company_name"],
        role=analysis["role"],
        created_at=analysis["created_at"],
    )


@router.patch("/{analysis_id}/review")
async def update_section_review(
    analysis_id: int,
    update: SectionReviewUpdate,
    db: asyncpg.Connection = Depends(get_db),
):
    exists = await db.fetchval(
        "SELECT 1 FROM analyses WHERE id = $1", analysis_id
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Analysis not found")

    await db.execute(
        """
        INSERT INTO section_reviews
            (analysis_id, suggestion_id, status, edited_content)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (analysis_id, suggestion_id)
        DO UPDATE SET status = $3, edited_content = $4
        """,
        analysis_id,
        update.suggestion_id,
        update.status,
        update.edited_content,
    )

    logger.info(
        f"Review saved: analysis={analysis_id}, "
        f"suggestion={update.suggestion_id}, status={update.status}"
    )
    return {"ok": True}


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: asyncpg.Connection = Depends(get_db),
):
    deleted = await db.fetchval(
        "DELETE FROM analyses WHERE id = $1 RETURNING id", analysis_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"ok": True}