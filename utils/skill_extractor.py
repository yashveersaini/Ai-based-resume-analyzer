import re
from data.skills_db import SKILL_BANK


def extract_skills(text: str) -> list[str]:
    """Extract skills from text by matching against skill bank."""
    text_lower = text.lower()
    found_skills = []

    for skill in SKILL_BANK:
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return list(set(found_skills))  