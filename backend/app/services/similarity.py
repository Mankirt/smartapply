import logging
from app.services.embeddings import generate_embedding

logger = logging.getLogger(__name__)


async def find_similar_sections(
    jd_text: str,
    resume_id: int,
    db,
    top_k: int = 5,
) -> list[dict]:
    jd_embedding = generate_embedding(jd_text)

    rows = await db.fetch(
        """
        SELECT
            section_type,
            title,
            content,
            1 - (embedding <=> $1::vector) AS similarity
        FROM resume_sections
        WHERE resume_id = $2
        ORDER BY embedding <=> $1::vector
        LIMIT $3
        """,
        str(jd_embedding),
        resume_id,
        top_k,
    )

    results = [
        {
            "section_type": r["section_type"],
            "title": r["title"],
            "content": r["content"],
            "similarity": round(float(r["similarity"]), 4),
        }
        for r in rows
    ]

    logger.info(
        f"Similarity search: resume={resume_id}, "
        f"top match={results[0]['section_type'] if results else 'none'} "
        f"score={results[0]['similarity'] if results else 0}"
    )

    return results