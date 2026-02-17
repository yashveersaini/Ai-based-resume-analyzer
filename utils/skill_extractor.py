import spacy
import re

nlp = spacy.load("en_core_web_sm")

# Predefined skill bank (expand as needed)
SKILL_BANK = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "sql", "mysql", "postgresql", "mongodb", "sqlite", "redis", "cassandra",
    "html", "css", "react", "angular", "vue", "node.js", "express", "django",
    "flask", "fastapi", "spring", "spring boot", "hibernate",
    "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "jenkins",
    "git", "github", "gitlab", "bitbucket", "linux", "bash", "powershell",
    "machine learning", "deep learning", "nlp", "computer vision",
    "tensorflow", "pytorch", "keras", "scikit-learn", "pandas", "numpy",
    "tableau", "power bi", "excel", "data analysis", "data visualization",
    "rest api", "graphql", "microservices", "agile", "scrum", "jira",
    "communication", "leadership", "problem solving", "teamwork",
]

def extract_skills(text: str) -> list[str]:
    """Extract skills from text by matching against skill bank."""
    text_lower = text.lower()
    found_skills = []

    for skill in SKILL_BANK:
        # Use word-boundary matching to avoid partial matches
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text_lower):
            found_skills.append(skill)

    return list(set(found_skills))  # deduplicate