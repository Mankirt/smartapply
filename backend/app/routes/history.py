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
            "SELECT * FROM analyses ORDER BY created_at DESC LIMIT 20"
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

    # load saved suggestions grouped by section
    suggestion_rows = await db.fetch(
        """
        SELECT * FROM section_suggestions
        WHERE analysis_id = $1
        ORDER BY section_type, id
        """,
        analysis_id,
    )

    # group suggestions by section_type
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
            "original": s["original"],
            "improved": s["improved"],
            "reason": s["reason"],
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
    """
    Step 6 — save user's Accept/Edit/Ignore decision for a section.
    Uses ON CONFLICT to upsert — update if exists, insert if not.
    """
    exists = await db.fetchval(
        "SELECT 1 FROM analyses WHERE id = $1", analysis_id
    )
    if not exists:
        raise HTTPException(status_code=404, detail="Analysis not found")

    await db.execute(
        """
        INSERT INTO section_reviews
            (analysis_id, section_type, status, edited_content)
        VALUES ($1, $2, $3, $4)
        ON CONFLICT (analysis_id, section_type)
        DO UPDATE SET status = $3, edited_content = $4
        """,
        analysis_id,
        update.section_type,
        update.status,
        update.edited_content,
    )

    logger.info(
        f"Section review: analysis={analysis_id}, "
        f"section={update.section_type}, status={update.status}"
    )
    return {"ok": True}


@router.delete("/{analysis_id}")
async def delete_analysis(
    analysis_id: int,
    db: asyncpg.Connection = Depends(get_db),
):
    deleted = await db.fetchval(
        "DELETE FROM analyses WHERE id = $1 RETURNING id",
        analysis_id
    )
    if not deleted:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return {"ok": True}

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

    section_rows = await db.fetch(
        "SELECT * FROM resume_sections WHERE resume_id = $1 ORDER BY order_index",
        analysis["resume_id"],
    )

    import json
    return AnalysisResponse(
        id=analysis["id"],
        resume_id=analysis["resume_id"],
        fit_score=analysis["fit_score"],
        matching_skills=json.loads(analysis["matching_skills"]),
        missing_keywords=json.loads(analysis["missing_keywords"]),
        summary=analysis["summary"],
        sections=[
            {
                "section_type": r["section_type"],
                "section_title": r["title"],
                "similarity_score": 0.0,
                "suggestions": [],
                "status": "pending",
            }
            for r in section_rows
        ],
        created_at=analysis["created_at"],
    )