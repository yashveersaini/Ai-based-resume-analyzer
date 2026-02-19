import os
from sentence_transformers import SentenceTransformer, util
from utils.skill_extractor import extract_skills

MODEL_NAME = "all-MiniLM-L6-v2"
LOCAL_MODEL_PATH = "./models/all-MiniLM-L6-v2"

# Create models directory if not exists
os.makedirs("./models", exist_ok=True)

# Load model (local if exists, otherwise download and save)
if os.path.exists(LOCAL_MODEL_PATH):
    print("Loading model from local folder...")
    model = SentenceTransformer(LOCAL_MODEL_PATH)
else:
    print("Downloading model from Hugging Face...")
    model = SentenceTransformer(MODEL_NAME)
    model.save(LOCAL_MODEL_PATH)
    print("Model saved locally!")

# -----------------------------
THRESHOLD = 0.6  


def compute_ats_score(resume_text: str, job_description: str) -> dict:
    """
    Compare resume skills vs JD skills using semantic similarity.
    """

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(job_description)

    # ── Edge cases ──
    if not jd_skills:
        return {
            "score": 0,
            "resume_skills": sorted(resume_skills),
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
    jd_embeddings = model.encode(jd_skills, convert_to_tensor=True)
    resume_embeddings = model.encode(resume_skills, convert_to_tensor=True)

    matched = []
    missing = []

    for i, jd_skill in enumerate(jd_skills):
        similarities = util.cos_sim(jd_embeddings[i], resume_embeddings)[0]
        best_score = float(similarities.max())

        if best_score >= THRESHOLD:
            matched.append(jd_skill)
        else:
            missing.append(jd_skill)

    score = round((len(matched) / len(jd_skills)) * 100, 2)

    return {
        "score": score,
        "resume_skills": sorted(resume_skills),
        "matched_skills": sorted(matched),
        "missing_skills": sorted(missing),
        "error": None
    }
