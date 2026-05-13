import json
import logging
from anthropic import Anthropic
from app.config.settings import get_settings

logger = logging.getLogger(__name__)
client = Anthropic()
settings = get_settings()
MODEL = "claude-sonnet-4-20250514"


def _analyze_fit(
    resume_text: str,
    jd_text: str,
    similar_sections: list[dict]
) -> dict:
    context = "\n\n".join(
        f"[{s['section_type'].upper()} — similarity: {s['similarity']}]\n{s['content']}"
        for s in similar_sections
    )

    prompt = f"""You are a technical recruiter analyzing resume-job fit.

JOB DESCRIPTION:
{jd_text}

MOST RELEVANT RESUME SECTIONS:
{context}

FULL RESUME:
{resume_text}

Return ONLY a valid JSON object. No markdown, no explanation, no preamble.

{{
  "fit_score": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "summary": "<2-3 sentences: overall assessment>"
}}"""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    raw = _extract_json(raw)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        logger.warning("Claude returned invalid JSON, retrying...")
        return _analyze_fit_retry(resume_text, jd_text)


def _analyze_fit_retry(resume_text: str, jd_text: str) -> dict:
    prompt = f"""Resume: {resume_text[:2000]}
Job Description: {jd_text[:2000]}

Respond with ONLY this JSON, no other text:
{{"fit_score": 0, "matching_skills": [], "missing_keywords": [], "summary": ""}}

Fill in real values. Return ONLY the JSON object."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}]
    )
    return json.loads(response.content[0].text.strip())


def _suggest_section_improvements(
    section_content: str,
    section_type: str,
    jd_text: str,
) -> list[dict]:
    prompt = f"""You are a resume coach improving a resume section to match a job description.

JOB DESCRIPTION:
{jd_text[:1500]}

RESUME SECTION ({section_type.upper()}):
{section_content}

For each bullet that could be stronger, suggest an improvement.
Focus on: quantifying impact, using JD keywords naturally, showing scope.

Return ONLY a valid JSON array. No markdown, no explanation.

[
  {{
    "original": "<exact original bullet>",
    "improved": "<rewritten version>",
    "reason": "<one sentence: why this helps for this specific role>"
  }}
]

Return empty array [] if no improvements needed."""

    response = client.messages.create(
        model=MODEL,
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}]
    )

    raw = response.content[0].text.strip()
    raw = _extract_json(raw)
    try:
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except json.JSONDecodeError:
        logger.warning(f"Invalid JSON for section suggestions: {section_type}")
        return []


async def run_analysis_pipeline(
    resume_text: str,
    jd_text: str,
    sections: list,
    similar_sections: list[dict],
) -> dict:
    fit_result = _analyze_fit(resume_text, jd_text, similar_sections)

    section_analyses = []
    for section in sections:
        similarity = next(
            (s["similarity"] for s in similar_sections
             if s["section_type"] == section["section_type"]),
            0.0,
        )

        if similarity > 0.3 or section["section_type"] in ("experience", "skills"):
            suggestions = _suggest_section_improvements(
                section_content=section["content"],
                section_type=section["section_type"],
                jd_text=jd_text,
            )
        else:
            suggestions = []

        section_analyses.append({
            "section_type": section["section_type"],
            "section_title": section["title"],
            "similarity_score": similarity,
            "suggestions": suggestions,
            "status": "pending",
        })

    return {
        "fit_score": fit_result["fit_score"],
        "matching_skills": fit_result["matching_skills"],
        "missing_keywords": fit_result["missing_keywords"],
        "summary": fit_result["summary"],
        "sections": section_analyses,
    }

def _extract_json(raw: str) -> str:
    raw = raw.strip()
    if raw.startswith("```"):
        lines = raw.split("\n")
        raw = "\n".join(lines[1:-1])
    return raw.strip()

async def stream_analysis(
    jd_text: str,               
    similar_sections: list[dict],
):
    context = "\n\n".join(
        f"[{s['section_type'].upper()}]\n{s['content']}"
        for s in similar_sections
    )

    prompt = f"""Analyze this resume against the job description.

JOB DESCRIPTION:
{jd_text}

RELEVANT RESUME SECTIONS:
{context}

Provide: fit score (0-100), matching skills, missing keywords, and assessment."""

    with client.messages.stream(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for text in stream.text_stream:
            yield f"data: {text}\n\n"