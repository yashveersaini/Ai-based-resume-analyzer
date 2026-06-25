from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import requests
from io import BytesIO
from utils.database import create_tables



# Import database functions
from utils.database import (
    get_user_by_id,
    save_resume, get_user_resume, delete_user_resume
)
from utils.clerk_auth import init_clerk_config, login_required, page_login_required, resolve_session_user

# Import resume analysis functions
from utils.document_parser import extract_text_from_document, is_supported_format
from utils.ats_scorer import compute_ats_score
from utils.skill_extractor import extract_skills
from utils.hybrid_recommender import get_top5_recommendations

load_dotenv()

create_tables()

app = Flask(__name__, 
            template_folder='frontend',
            static_folder='frontend/static')

# CONFIGURATION
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
init_clerk_config(app)

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  
app.config['ALLOWED_EXTENSIONS'] = {'.pdf', '.docx'}


# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)


@app.context_processor
def inject_clerk_config():
    return {
        'clerk_publishable_key': os.getenv('CLERK_PUBLISHABLE_KEY', ''),
        'clerk_frontend_api': os.getenv('CLERK_FRONTEND_API', ''),
    }


def get_file_extension(filename):
    """Get file extension in lowercase with dot."""
    return os.path.splitext(filename.lower())[1]


def delete_old_resume_file(user_id):
    """Delete the old resume from Cloudinary if it exists."""
    resume = get_user_resume(user_id)

    if resume and resume.get("public_id"):
        try:
            cloudinary.uploader.destroy(
                resume["public_id"],
                resource_type="raw"
            )
            print(f"Deleted old resume from Cloudinary: {resume['public_id']}")
        except Exception as e:
            print(f"⚠ Error deleting resume from Cloudinary: {e}")


# FRONTEND ROUTES (Serve HTML Pages)
@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


@app.route("/health")
def health():
    return {"status": "ok"}


@app.route('/login')
def login_page():
    """Login page."""
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    """Signup page."""
    return render_template('signup.html')


@app.route('/dashboard')
def dashboard_page():
    """Dashboard page (requires login)."""
    auth_redirect = page_login_required()
    if auth_redirect:
        return auth_redirect
    return render_template('dashboard.html')


@app.route('/upload')
def upload_page():
    """Resume upload & analysis page (requires login)."""
    auth_redirect = page_login_required()
    if auth_redirect:
        return auth_redirect
    return render_template('upload.html')


@app.route('/data/<path:filename>')
def serve_data(filename):
    """Serve JSON files from data folder."""
    from flask import send_from_directory
    return send_from_directory('data', filename)


# AUTHENTICATION API ROUTES

@app.route('/api/clerk-config')
def api_clerk_config():
    """Expose Clerk frontend configuration to the browser."""
    return jsonify({
        'publishableKey': os.getenv('CLERK_PUBLISHABLE_KEY', ''),
        'frontendApi': os.getenv('CLERK_FRONTEND_API', ''),
    })


@app.route('/api/auth/sync', methods=['POST'])
def api_auth_sync():
    """Sync a verified Clerk session to the local Flask session."""
    user_id = resolve_session_user()
    if user_id is None:
        return jsonify({'error': 'Authentication required'}), 401

    user = get_user_by_id(user_id)
    if user is None:
        session.clear()
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'success': True,
        'user': {
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
        }
    })


@app.route('/api/logout', methods=['POST'])
def api_logout():
    """Handle user logout."""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out successfully'})


@app.route('/api/current-user', methods=['GET'])
@login_required
def api_current_user():
    """Get current logged-in user info."""
    user = get_user_by_id(session['user_id'])
    
    if user is None:
        session.clear()
        return jsonify({'error': 'User not found'}), 404
    
    # Check if user has a resume
    resume = get_user_resume(user['id'])
    
    return jsonify({
        'user': {
            'id':          user['id'],
            'name':        user['name'],
            'email':       user['email'],
            'has_resume':  resume is not None,
            'resume':      {
                'filename':    resume['filename'],
                'uploaded_at': resume['uploaded_at'].isoformat() if resume else None
            } if resume else None
        }
    })


# RESUME UPLOAD & MANAGEMENT

@app.route('/api/upload-resume', methods=['POST'])
@login_required
def api_upload_resume():
    """Upload and save user's resume to Cloudinary (replaces old one if exists)."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not is_supported_format(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are accepted'}), 400
    
    user_id = session['user_id']
    
    delete_old_resume_file(user_id)
    
    # Save new file to Cloudinary
    filename = secure_filename(file.filename)

    try:
        upload_result = cloudinary.uploader.upload(
            file,
            resource_type="raw",
            folder="resumes",
            public_id=f"user_{user_id}",
            overwrite=True
        )

        file_url = upload_result["secure_url"]
        public_id = upload_result["public_id"]
    except Exception as e:
        return jsonify({'error': f'Failed to upload to Cloudinary: {str(e)}'}), 500
    
    resume = save_resume(user_id, filename, file_url, public_id)
    
    if resume is None:
        try:
            cloudinary.uploader.destroy(public_id, resource_type="raw")
        except:
            pass
        return jsonify({'error': 'Failed to save resume to database'}), 500
    
    return jsonify({
        'success': True,
        'message': 'Resume uploaded successfully',
        'resume': {
            'filename':    resume['filename'],
            'uploaded_at': resume['uploaded_at'].isoformat()
        }
    })


@app.route('/api/get-resume', methods=['GET'])
@login_required
def api_get_resume():
    """Get current user's resume info."""
    user_id = session['user_id']
    resume  = get_user_resume(user_id)
    
    if resume is None:
        return jsonify({'error': 'No resume found'}), 404
    
    return jsonify({
        'resume': {
            'filename': resume['filename'],
            'uploaded_at': resume['uploaded_at'].isoformat(),
            'file_url': resume['file_path']
        }
    })


@app.route('/api/delete-resume', methods=['DELETE'])
@login_required
def api_delete_resume():
    """Delete current user's resume from Cloudinary and database."""
    user_id = session['user_id']
    
    # Delete from Cloudinary
    delete_old_resume_file(user_id)
    
    # Delete from database
    success = delete_user_resume(user_id)
    
    if success:
        return jsonify({'success': True, 'message': 'Resume deleted successfully'})
    else:
        return jsonify({'error': 'No resume to delete'}), 404


# RESUME ANALYSIS API (Protected Routes)
@app.route("/api/analyze", methods=["POST"])
@login_required
def api_analyze():
    """ATS Score analysis (downloads resume from Cloudinary and analyzes)."""
    user_id = session['user_id']
    
    # Get user's uploaded resume
    resume_db = get_user_resume(user_id)

    if resume_db is None:
        return jsonify({"error": "No resume uploaded. Please upload your resume first."}), 400
    
    job_description = request.form.get("job_description", "").strip()
    
    if not job_description:
        return jsonify({"error": "Job description is required"}), 400
    
    try:
        # Download resume from Cloudinary URL
        response = requests.get(resume_db['file_path'], timeout=10)

        if response.status_code != 200:
            return jsonify({"error": "Failed to download resume from Cloudinary"}), 500

        file_stream = BytesIO(response.content)

        resume_text = extract_text_from_document(file_stream, resume_db['filename'])

    except Exception as e:
        return jsonify({"error": f"Failed to read resume: {str(e)}"}), 500
    
    result = compute_ats_score(resume_text, job_description)
    return jsonify(result)


@app.route("/api/suggest", methods=["POST"])
@login_required
def api_suggest():
    """Job role suggestion using hybrid recommender (downloads resume from Cloudinary)."""
    user_id = session['user_id']
    
    resume_db = get_user_resume(user_id)

    if resume_db is None:
        return jsonify({"error": "No resume uploaded. Please upload your resume first."}), 400

    try:
        response = requests.get(resume_db['file_path'], timeout=10)

        if response.status_code != 200:
            return jsonify({"error": "Failed to download resume from Cloudinary"}), 500

        file_stream = BytesIO(response.content)

        resume_text = extract_text_from_document(file_stream, resume_db['filename'])

    except Exception as e:
        return jsonify({"error": f"Failed to read resume: {str(e)}"}), 500

    try:
        recommendations = get_top5_recommendations(resume_text)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    resume_skills = extract_skills(resume_text)

    return jsonify({
        "resume_skills":    sorted(resume_skills),
        "recommendations":  recommendations,
        "error":            None
    })



if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=5000)