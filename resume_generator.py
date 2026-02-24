"""
resume_generator.py
-------------------
Generates an ATS-friendly PDF resume using reportlab.
Call generate_resume() and it returns raw PDF bytes ready for
st.download_button() in Streamlit.
"""

from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


# ── Colour palette ──────────────────────────────────────────────────────────
DARK_BLUE  = colors.HexColor("#1A237E")
MID_BLUE   = colors.HexColor("#3949AB")
LIGHT_GREY = colors.HexColor("#F5F5F5")
ACCENT     = colors.HexColor("#00897B")


def _styles():
    base = getSampleStyleSheet()
    custom = {
        "name": ParagraphStyle(
            "name", parent=base["Title"],
            fontSize=22, textColor=DARK_BLUE,
            spaceAfter=2, alignment=TA_CENTER, fontName="Helvetica-Bold"
        ),
        "contact": ParagraphStyle(
            "contact", parent=base["Normal"],
            fontSize=9, textColor=colors.grey,
            spaceAfter=6, alignment=TA_CENTER
        ),
        "section": ParagraphStyle(
            "section", parent=base["Heading2"],
            fontSize=11, textColor=DARK_BLUE,
            spaceBefore=10, spaceAfter=2, fontName="Helvetica-Bold",
            borderPad=2
        ),
        "body": ParagraphStyle(
            "body", parent=base["Normal"],
            fontSize=9.5, leading=14, spaceAfter=3
        ),
        "skill_tag": ParagraphStyle(
            "skill_tag", parent=base["Normal"],
            fontSize=9, textColor=MID_BLUE, fontName="Helvetica-Bold"
        ),
        "bullet": ParagraphStyle(
            "bullet", parent=base["Normal"],
            fontSize=9.5, leading=14, spaceAfter=2,
            leftIndent=12, bulletIndent=4
        ),
    }
    return custom


def _hr(color=MID_BLUE, thickness=0.8):
    return HRFlowable(width="100%", thickness=thickness, color=color, spaceAfter=4)


def generate_resume(
    name: str,
    email: str,
    phone: str,
    college: str,
    branch: str,
    cgpa: float,
    skills: list[str],
    projects: list[dict],   # [{"title": ..., "desc": ...}]
    internships: list[dict],# [{"role": ..., "company": ..., "duration": ..., "desc": ...}]
    achievements: list[str],
    linkedin: str = "",
    github: str = "",
) -> bytes:
    """
    Build and return PDF bytes for an ATS-optimised resume.

    projects  : list of dicts with keys 'title' and 'desc'
    internships: list of dicts with keys 'role', 'company', 'duration', 'desc'
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm
    )
    S = _styles()
    story = []

    # ── Header ───────────────────────────────────────────────────────────────
    story.append(Paragraph(name.upper(), S["name"]))
    contact_parts = [x for x in [email, phone, linkedin, github] if x]
    story.append(Paragraph("  |  ".join(contact_parts), S["contact"]))
    story.append(_hr(DARK_BLUE, 1.5))

    # ── Education ────────────────────────────────────────────────────────────
    story.append(Paragraph("EDUCATION", S["section"]))
    story.append(_hr())
    edu_data = [
        [Paragraph(f"<b>{college}</b>", S["body"]),
         Paragraph(f"CGPA: <b>{cgpa}/10</b>", S["body"])],
        [Paragraph(branch, S["body"]), Paragraph("", S["body"])],
    ]
    edu_table = Table(edu_data, colWidths=["70%", "30%"])
    edu_table.setStyle(TableStyle([
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(edu_table)
    story.append(Spacer(1, 6))

    # ── Technical Skills ─────────────────────────────────────────────────────
    story.append(Paragraph("TECHNICAL SKILLS", S["section"]))
    story.append(_hr())
    # Group skills in rows of 5
    chunk = 5
    rows = [skills[i:i+chunk] for i in range(0, len(skills), chunk)]
    for row in rows:
        story.append(Paragraph("  •  ".join(row), S["skill_tag"]))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 4))

    # ── Projects ─────────────────────────────────────────────────────────────
    if projects:
        story.append(Paragraph("PROJECTS", S["section"]))
        story.append(_hr())
        for p in projects:
            story.append(Paragraph(f"<b>{p['title']}</b>", S["body"]))
            for line in p["desc"].strip().split("\n"):
                if line.strip():
                    story.append(Paragraph(f"• {line.strip()}", S["bullet"]))
            story.append(Spacer(1, 4))

    # ── Internships / Experience ──────────────────────────────────────────────
    if internships:
        story.append(Paragraph("INTERNSHIPS / EXPERIENCE", S["section"]))
        story.append(_hr())
        for intern in internships:
            row = [
                Paragraph(f"<b>{intern['role']}</b> — {intern['company']}", S["body"]),
                Paragraph(intern.get("duration", ""), S["body"]),
            ]
            t = Table([row], colWidths=["70%", "30%"])
            t.setStyle(TableStyle([("ALIGN", (1, 0), (1, 0), "RIGHT"),
                                   ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
            story.append(t)
            for line in intern.get("desc", "").strip().split("\n"):
                if line.strip():
                    story.append(Paragraph(f"• {line.strip()}", S["bullet"]))
            story.append(Spacer(1, 4))

    # ── Achievements ─────────────────────────────────────────────────────────
    if achievements:
        story.append(Paragraph("ACHIEVEMENTS & CERTIFICATIONS", S["section"]))
        story.append(_hr())
        for ach in achievements:
            if ach.strip():
                story.append(Paragraph(f"• {ach.strip()}", S["bullet"]))

    doc.build(story)
    return buf.getvalue()


# ---------- quick smoke-test ----------
if __name__ == "__main__":
    pdf_bytes = generate_resume(
        name="Ashutosh Shri Mishra",
        email="ashutosh@example.com",
        phone="+91-9876543210",
        college="NIT Agartala",
        branch="B.Tech Computer Science & Engineering  |  2022 – 2026",
        cgpa=8.5,
        skills=["Python", "Machine Learning", "XGBoost", "Scikit-learn",
                "Pandas", "NumPy", "SQL", "Power BI", "Streamlit", "Git"],
        projects=[
            {"title": "SmartPlace – AI Placement Portal",
             "desc": "Built Streamlit MVP with TF-IDF job matching engine\n"
                     "Integrated reportlab resume generator & ML fit scoring\n"
                     "Achieved 95% skill-match accuracy on test dataset"},
            {"title": "Jal-Drishti – Water Intelligence Dashboard",
             "desc": "Predicted AI data-centre water usage with LSTM models\n"
                     "Visualised India sector-wise water data using Power BI"},
        ],
        internships=[
            {"role": "Data Science Intern", "company": "Statistella",
             "duration": "Jan 2025 – Mar 2025",
             "desc": "Ranked Top-5 in BASH 8.0 Round-2 ML competition\n"
                     "Built ensemble XGBoost + LightGBM pipeline"}
        ],
        achievements=[
            "TECHNOVUS Hackathon – SmartPlace Finalist",
            "BASH 8.0 by Statistella – Top 5 Nationally",
            "East India Blockchain Summit 2025 – Speaker",
        ],
        linkedin="linkedin.com/in/ashutosh-mishra",
        github="github.com/ashutosh-mishra",
    )
    with open("sample_resume.pdf", "wb") as f:
        f.write(pdf_bytes)
    print("✅  sample_resume.pdf generated successfully.")
