import io
import logging
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_LEFT

logger = logging.getLogger(__name__)

# colors
EMERALD = HexColor('#065f46')
GRAY = HexColor('#6b7280')
LIGHT_GRAY = HexColor('#e5e7eb')
BLACK = HexColor('#111827')


def generate_suggestions_pdf(
    company_name: str,
    role: str | None,
    resume_filename: str | None,
    sections: list[dict],
) -> bytes:
    """
    Generate a PDF of accepted/edited suggestions.
    Returns PDF as bytes.
    """
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    styles = getSampleStyleSheet()

    # custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Normal'],
        fontSize=20,
        textColor=EMERALD,
        fontName='Helvetica-Bold',
        spaceAfter=15,
    )

    subtitle_style = ParagraphStyle(
        'Subtitle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=GRAY,
        fontName='Helvetica',
        spaceAfter=2,
    )

    section_heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Normal'],
        fontSize=13,
        textColor=EMERALD,
        fontName='Helvetica-Bold',
        spaceBefore=16,
        spaceAfter=8,
    )

    label_style = ParagraphStyle(
        'Label',
        parent=styles['Normal'],
        fontSize=8,
        textColor=GRAY,
        fontName='Helvetica-Bold',
        spaceAfter=3,
        leading=12,
    )

    original_style = ParagraphStyle(
        'Original',
        parent=styles['Normal'],
        fontSize=10,
        textColor=GRAY,
        fontName='Helvetica-Oblique',
        spaceAfter=6,
        leading=14,
    )

    improved_style = ParagraphStyle(
        'Improved',
        parent=styles['Normal'],
        fontSize=10,
        textColor=BLACK,
        fontName='Helvetica',
        spaceAfter=4,
        leading=15,
    )

    reason_style = ParagraphStyle(
        'Reason',
        parent=styles['Normal'],
        fontSize=9,
        textColor=GRAY,
        fontName='Helvetica-Oblique',
        spaceAfter=12,
        leading=13,
    )

    # build content
    content = []

    # header
    content.append(Paragraph("SmartApply", title_style))
    content.append(Paragraph("Resume Suggestions", subtitle_style))

    target = company_name
    if role:
        target += f" — {role}"
    content.append(Paragraph(target, subtitle_style))

    if resume_filename:
        content.append(Paragraph(f"Resume: {resume_filename}", subtitle_style))

    content.append(Spacer(1, 8))
    content.append(HRFlowable(width="100%", thickness=1, color=LIGHT_GRAY))
    content.append(Spacer(1, 4))

    # count accepted suggestions
    total = sum(
        1 for section in sections
        for s in section.get("suggestions", [])
        if s.get("status") in ("accepted", "edited")
    )

    if total == 0:
        content.append(Spacer(1, 20))
        content.append(Paragraph(
            "No accepted suggestions found. Accept or edit suggestions in SmartApply first.",
            subtitle_style
        ))
    else:
        content.append(Paragraph(
            f"{total} suggestion{'s' if total != 1 else ''} accepted",
            subtitle_style
        ))

        for section in sections:
            accepted = [
                s for s in section.get("suggestions", [])
                if s.get("status") in ("accepted", "edited")
            ]
            if not accepted:
                continue

            # section heading
            content.append(Paragraph(
                section.get("section_title", "Section").upper(),
                section_heading_style
            ))
            content.append(HRFlowable(width="100%", thickness=0.5, color=LIGHT_GRAY))

            for suggestion in accepted:
                # original (strikethrough effect via gray italic)
                content.append(Spacer(1, 8))
                content.append(Paragraph("ORIGINAL", label_style))
                content.append(Paragraph(
                    suggestion.get("original", ""),
                    original_style
                ))

                # improved
                content.append(Paragraph("SUGGESTED", label_style))
                improved = (
                    suggestion.get("edited_content")
                    or suggestion.get("improved", "")
                )
                content.append(Paragraph(improved, improved_style))

                # reason
                content.append(Paragraph(
                    f"Why: {suggestion.get('reason', '')}",
                    reason_style
                ))

                content.append(HRFlowable(
                    width="100%", thickness=0.5,
                    color=LIGHT_GRAY, spaceAfter=4
                ))

    doc.build(content)
    buffer.seek(0)
    return buffer.read()