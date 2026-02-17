from flask import Flask, render_template, request, jsonify
from utils.pdf_parser import extract_text_from_pdf
from utils.ats_scorer import compute_ats_score

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "No resume file uploaded"}), 400

    resume_file = request.files["resume"]
    job_description = request.form.get("job_description", "").strip()

    if resume_file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not job_description:
        return jsonify({"error": "Job description is required"}), 400

    # Extract resume text from PDF
    try:
        resume_text = extract_text_from_pdf(resume_file)
    except Exception as e:
        return jsonify({"error": f"Failed to read PDF: {str(e)}"}), 500

    # Compute ATS score
    result = compute_ats_score(resume_text, job_description)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)