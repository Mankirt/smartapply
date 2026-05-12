import logging
from fastapi import APIRouter, Depends, HTTPException
import asyncpg

from app.config.database import get_db
from app.models.schemas import AnalysisSummary, SectionReviewUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/", response_model=list[AnalysisSummary])
async def list_analyses(
    resume_id: int | None = None,
    db: asyncpg.Connection = Depends(get_db),
):
    """
    List past analyses.
    Optional resume_id filter — powers the history panel.
    """
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
            created_at=r["created_at"],
        )
        for r in rows
    ]


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