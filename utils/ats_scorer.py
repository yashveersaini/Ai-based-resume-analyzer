from sentence_transformers import SentenceTransformer, util
from utils.skill_extractor import extract_skills

# Load once at module level (cached after first load)
model = SentenceTransformer("all-MiniLM-L6-v2")

def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Compare resume skills vs JD skills using semantic similarity.
    Returns score, matched skills, and missing skills.
    """
    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    if not jd_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "error": "No recognizable skills found in job description."
        }

    if not resume_skills:
        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": jd_skills,
            "error": "No recognizable skills found in resume."
        }

    matched = []
    missing = []

    # For each JD skill, check if resume has a semantically similar skill
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)

    THRESHOLD = 0.6  # Cosine similarity threshold

    for i, jd_skill in enumerate(jd_skills):
        # Compare this JD skill against all resume skills
        similarities = util.cos_sim(jd_embeddings[i], resume_embeddings)[0]
        best_score = float(similarities.max())

        if best_score >= THRESHOLD:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)

    score = round((len(matched) / len(jd_skills)) * 100, 2)

    return {
        "score": score,
        "matched_skills": matched,
        "missing_skills": missing,
        "error": None
    }