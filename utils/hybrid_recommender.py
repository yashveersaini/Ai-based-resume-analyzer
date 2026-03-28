import pickle
import numpy as np
import json
import os
from utils.document_parser import cleanResume


BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR  = os.path.join(BASE_DIR, 'models')


tfidf          = pickle.load(open(os.path.join(MODEL_DIR, 'tfidf.pkl'), 'rb'))
clf            = pickle.load(open(os.path.join(MODEL_DIR, 'clf_logistics.pkl'), 'rb'))
label_encoder  = pickle.load(open(os.path.join(MODEL_DIR, 'label_encoder.pkl'), 'rb'))


def predict_job_role(txt, k):
    my_resume       = cleanResume(txt)
    input_features  = tfidf.transform([my_resume])
    prediction_prob = clf.predict_proba(input_features)
    top_k_idx       = prediction_prob.argsort()[:, -k:][:, ::-1]
    top_k_labels    = [label_encoder.inverse_transform(row) for row in top_k_idx]
    top_k_probs     = np.take_along_axis(prediction_prob, top_k_idx, axis=1)
    return top_k_labels, top_k_probs


#  TRENDING ROLE MAP  

with open('data/trending_role_map.json', 'r') as f:
    TRENDING_ROLE_MAP = json.load(f)


def _confidence_label(score: float) -> str:
    """Converts a numeric score to a human-readable confidence label."""
    if score >= 0.60:
        return "High"
    elif score >= 0.30:
        return "Medium"
    else:
        return "Low"


#  TRENDING MAP SCORER
#  Returns matched trending roles sorted by match strength.

def _score_trending(cleaned_text: str) -> list[dict]:
    """
    Scans cleaned resume text against TRENDING_ROLE_MAP.
    Returns all roles that meet min_matches, sorted by score desc.
    Score = (matched_keywords / total_keywords) + trending_score_boost
    """
    results = []

    for role, config in TRENDING_ROLE_MAP.items():
        keywords      = config["keywords"]
        min_matches   = config["min_matches"]
        boost         = config.get("trending_score_boost", 0.0)
        parent        = config.get("parent_category", "")

        matched = [kw for kw in keywords if kw in cleaned_text]

        if len(matched) >= min_matches:
            base_score = len(matched) / len(keywords)
            final_score = round(base_score + boost, 4)

            results.append({
                "role":           role,
                "score":          final_score,
                "source":         "Trending map",
                "parent_category": parent,
                "matched_skills": matched[:5],          
                "confidence":     _confidence_label(final_score),
            })

    return sorted(results, key=lambda x: x["score"], reverse=True)


def _get_ml_predictions(cleaned_text: str, top_n: int = 5) -> list[dict]:
    """
    Calls your LR model and returns results in the same
    dict shape as _score_trending() for easy merging.
    NOTE: cleaned_text is passed directly (already cleaned).
    """
    input_features  = tfidf.transform([cleaned_text])
    prediction_prob = clf.predict_proba(input_features)

    top_k_idx    = prediction_prob.argsort()[:, -top_n:][:, ::-1]
    top_k_labels = label_encoder.inverse_transform(top_k_idx[0])
    top_k_probs  = np.take_along_axis(prediction_prob, top_k_idx, axis=1)[0]

    results = []
    for label, prob in zip(top_k_labels, top_k_probs):
        results.append({
            "role":            label,
            "score":           round(float(prob), 4),
            "source":          "ML model",
            "parent_category": label,          
            "matched_skills":  [],             
            "confidence":      _confidence_label(float(prob)),
        })

    return results


#     SMART MERGE  - Dynamic split based on what fired
#
#     Scenario A  trending ≥ 2  →  top 3 trending + top 2 ML
#     Scenario B  trending == 1 →  top 1 trending + top 4 ML
#     Scenario C  trending == 0 →  top 5 ML only

def _merge(trending_results: list[dict],
           ml_results:       list[dict]) -> list[dict]:

    t = len(trending_results)

    if t >= 2:
        pool = trending_results[:3] + ml_results[:2]
    elif t == 1:
        pool = trending_results[:1] + ml_results[:4]
    else:
        pool = ml_results[:3]

    seen: dict[str, dict] = {}
    for item in pool:
        key = item["role"].lower().strip()
        if key not in seen or item["score"] > seen[key]["score"]:
            seen[key] = item

    ranked = sorted(seen.values(), key=lambda x: x["score"], reverse=True)
    return ranked[:5]


def get_top5_recommendations(resume_text: str) -> list[dict]:
    """
    Main entry point.

    Parameters
    ----------
    resume_text : str
        Raw resume text (uncleaned).

    Returns
    -------
    list[dict]  — exactly 5 recommendations, each containing:
        rank            int    1–5
        role            str    job role title
        score           float  0.0–1.0+ (trending roles can exceed 1.0 due to boost)
        confidence      str    High / Medium / Low
        source          str    "Trending map" or "ML model"
        parent_category str    original dataset category it belongs to
        matched_skills  list   skills that triggered this recommendation (trending only)
    """
    cleaned          = cleanResume(resume_text)
    trending_results = _score_trending(cleaned)
    ml_results       = _get_ml_predictions(cleaned, top_n=5)
    merged           = _merge(trending_results, ml_results)

    # Add rank numbers
    for i, item in enumerate(merged, 1):
        item["rank"] = i

    return merged


def display_recommendations(results: list[dict]) -> None:
    """Pretty-prints the top 5 recommendations to terminal."""
    print("\n" + "=" * 58)
    print("  TOP 5 JOB ROLE RECOMMENDATIONS")
    print("=" * 58)

    source_tag = {
        "Trending map": "[TRENDING]",
        "ML model":     "[ML MODEL]",
    }

    for r in results:
        tag  = source_tag.get(r["source"], "")
        conf = r["confidence"]
        conf_bar = {"High": "3", "Medium": "2", "Low": "1"}.get(conf, "")

        print(f"\n  #{r['rank']}  {r['role']}")
        print(f"      Source     : {r['source']}  {tag}")
        print(f"      Category   : {r['parent_category']}")
        print(f"      Score      : {r['score']:.4f}  {conf_bar}  ({conf})")

        if r["matched_skills"]:
            skills_str = ", ".join(r["matched_skills"])
            print(f"      Evidence   : {skills_str}")
        else:
            print(f"      Evidence   : (from trained ML model)")

    print("\n" + "=" * 58 + "\n")



if __name__ == "__main__":

    # Test 1
    resume_ai = """
    Experienced in building LLM applications using LangChain and LlamaIndex.
    Developed RAG pipelines with OpenAI GPT-4 and Gemini. Fine-tuned LLaMA
    models using LoRA/QLoRA. Built vector search with Pinecone and ChromaDB.
    Expertise in prompt engineering, function calling, and AI agents with
    LangGraph. Deployed FastAPI backends on AWS with MLflow tracking.
    """

    print("── RESUME 1: Modern AI Engineer ──")
    results = get_top5_recommendations(resume_ai)
    display_recommendations(results)

    # Test 2:
    resume_classic = """
    Python developer with expertise in machine learning and deep learning.
    Proficient in pandas, numpy, scikit-learn, TensorFlow, and Keras.
    Experience with data analysis, feature engineering, model evaluation,
    regression, classification, and clustering. Java backend development
    with Spring Boot and REST APIs. Version control with GitHub.
    """

    print("── RESUME 2: Classic ML / Python resume ──")
    results = get_top5_recommendations(resume_classic)
    display_recommendations(results)

    # Test 3: 
    resume_devops = """
    DevOps engineer with 5 years of experience. Expert in Docker, Kubernetes,
    Helm, Terraform, and Ansible. CI/CD pipelines with Jenkins and GitHub
    Actions. Cloud infrastructure on AWS (EKS, RDS, Lambda, S3). Monitoring
    with Prometheus, Grafana, and ELK stack. ArgoCD for GitOps workflows.
    """

    print("── RESUME 3: DevOps Engineer ──")
    results = get_top5_recommendations(resume_devops)
    display_recommendations(results)