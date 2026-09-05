"""
Medical report parsing & summarization (MVP item, spec Section 21).
Extracts text from uploaded documents, then summarizes via the model
router — routed through the AI safety gate since a "summarize my blood
test" request sits right at the education/diagnosis boundary.
"""

import io

from pypdf import PdfReader

from app.services.model_router import TaskComplexity, model_router
from app.services.safety_guard import apply_safety_gate


def extract_text(data: bytes, content_type: str) -> str:
    if content_type == "application/pdf":
        reader = PdfReader(io.BytesIO(data))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    if content_type.startswith("text/"):
        return data.decode("utf-8", errors="ignore")
    raise ValueError(f"Unsupported content type for extraction: {content_type}")


async def summarize_report(text: str, language: str = "en") -> str:
    blocked, disclaimer = apply_safety_gate(text)
    if blocked:
        return disclaimer

    prompt = (
        "Summarize the following medical report in plain, patient-friendly "
        f"language (target language: {language}). Explain what each key "
        "value means in general terms. Do not diagnose or recommend "
        "treatment — flag anything that looks urgent as 'discuss with your "
        "doctor'.\n\n"
        f"Report text:\n{text[:6000]}\n\nSummary:"
    )
    return await model_router.generate(prompt, complexity=TaskComplexity.MODERATE)
