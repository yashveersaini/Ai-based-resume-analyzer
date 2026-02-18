from sentence_transformers import SentenceTransformer, util
from utils.skill_extractor import extract_skills

# Load once at module level (cached after first load)
model = SentenceTransformer("all-MiniLM-L6-v2")

THRESHOLD = 0.6  # Cosine similarity threshold

def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Compare resume skills vs JD skills using semantic similarity.

    Returns:
        score         - ATS match % (based on JD skills covered)
        resume_skills - ALL skills found in the uploaded resume
        matched_skills- JD skills that the resume covers
        missing_skills- JD skills absent from the resume
        error         - error message string or None
    """

    # Extract ALL skills present in the resume (full picture for the user)
    resume_skills = extract_skills(resume_text)

    # Extract skills required by the job description
    jd_skills = extract_skills(job_description)

    # ── Edge cases ──
    if not jd_skills:
        return {
            "score": 0,
            "resume_skills": sorted(resume_skills),   # still return what we found
            "matched_skills": [],
            "missing_skills": [],
            "error": "No recognizable skills found in the job description."
        }

    if not resume_skills:
        return {
            "score": 0,
            "resume_skills": [],
            "matched_skills": [],
            "missing_skills": sorted(jd_skills),
            "error": "No recognizable skills found in the resume."
        }

    # ── Semantic similarity matching ──
    jd_embeddings     = model.encode(jd_skills,     convert_to_tensor=True)
    resume_embeddings = model.encode(resume_skills,  convert_to_tensor=True)

    matched = []
    missing = []

    for i, jd_skill in enumerate(jd_skills):
        # Compare each JD skill against every resume skill
        similarities = util.cos_sim(jd_embeddings[i], resume_embeddings)[0]
        best_score   = float(similarities.max())

        if best_score >= THRESHOLD:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)

    # Score = % of JD skills covered by the resume
    score = round((len(matched) / len(jd_skills)) * 100, 2)

    return {
        "score": score,
        "resume_skills": sorted(resume_skills),   # ALL skills from resume, sorted A-Z
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "error": None
    }