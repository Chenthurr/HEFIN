"""
AI Safety Safeguards (Spec Section 19): the platform must strictly
distinguish health education from autonomous diagnosis.
"""

import re

DIAGNOSTIC_PATTERNS = [
    r"\bdo i have\b",
    r"\bwhat disease\b",
    r"\bam i (?:sick|dying)\b",
    r"\bdiagnose me\b",
    r"\bwhat'?s wrong with me\b",
    r"\bshould i take .* (?:mg|dose|dosage)\b",
]

DISCLAIMER = (
    "I can share general health education, but I can't diagnose conditions "
    "or prescribe treatment. Please consult a licensed clinician for that."
)


def is_diagnostic_request(text: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered) for pattern in DIAGNOSTIC_PATTERNS)


def apply_safety_gate(text: str) -> tuple[bool, str | None]:
    if is_diagnostic_request(text):
        return True, DISCLAIMER
    return False, None
