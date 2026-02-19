from flask import Flask, render_template, request, jsonify
from utils.document_parser import extract_text_from_document, is_supported_format, get_supported_formats_string
from utils.ats_scorer import compute_ats_score
from utils.skill_extractor import extract_skills
from utils.job_suggester import suggest_jobs

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload


@app.route("/")
def index():
    return render_template("index.html")


# ── Feature 1: ATS Score ──
@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file     = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if resume_file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file format
    if not is_supported_format(resume_file.filename):
        return jsonify({
            "error": f"Unsupported file format. Supported: {get_supported_formats_string()}"
        }), 400
    
    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    try:
        resume_text = extract_text_from_document(resume_file, resume_file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to read document: {str(e)}"}), 500

    result = compute_ats_score(resume_text, job_description)
    return jsonify(result)


# ── Feature 2: Job Role Suggestion ──
@app.route("/suggest", methods=["POST"])
def suggest():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file = request.files["resume"]

    if resume_file.filename == "":
        return jsonify({"error": "No file selected"}), 400
    
    # Validate file format
    if not is_supported_format(resume_file.filename):
        return jsonify({
            "error": f"Unsupported file format. Supported: {get_supported_formats_string()}"
        }), 400

    try:
        resume_text = extract_text_from_document(resume_file, resume_file.filename)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"Failed to read document: {str(e)}"}), 500

    resume_skills = extract_skills(resume_text)

    if not resume_skills:
        return jsonify({"error": "No recognizable skills found in your resume."}), 400

    suggestions = suggest_jobs(resume_skills)

    return jsonify({
        "resume_skills": sorted(resume_skills),
        "suggestions":   suggestions,
        "error":         None
    })


if __name__ == "__main__":
    app.run(debug=True)