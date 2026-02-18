import spacy
import re
from data.skills_db import SKILL_BANK


nlp = spacy.load("en_core_web_sm")

def extract_skills(text: str) -> list[str]:
    """Extract skills from text by matching against skill bank."""
    text_lower = text.lower()
    found_skills = []

    for skill in SKILL_BANK:
        # Use word-boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return list(set(found_skills))  