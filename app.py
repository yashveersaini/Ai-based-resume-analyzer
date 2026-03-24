from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
import os
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import cloudinary
import cloudinary.uploader
import requests
from io import BytesIO

# Load environment variables from .env file
load_dotenv()

# Import database functions
from utils.database import (
    create_user, authenticate_user, get_user_by_id,
    save_resume, get_user_resume, delete_user_resume
)

# Import resume analysis functions
from utils.document_parser import extract_text_from_document, is_supported_format
from utils.ats_scorer import compute_ats_score
from utils.skill_extractor import extract_skills
from utils.hybrid_recommender import get_top5_recommendations

app = Flask(__name__, 
            template_folder='frontend',
            static_folder='frontend/static')

# ═══════════════════════════════════════════════════════════════
# CONFIGURATION
# ═══════════════════════════════════════════════════════════════

# Secret key for session management (CHANGE THIS in production!)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

# File upload configuration
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
app.config['ALLOWED_EXTENSIONS'] = {'.pdf', '.docx'}

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION DECORATOR
# ═══════════════════════════════════════════════════════════════

def login_required(f):
    """Decorator to protect routes that require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Authentication required'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

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
            print(f"✅ Deleted old resume from Cloudinary: {resume['public_id']}")
        except Exception as e:
            print(f"⚠ Error deleting resume from Cloudinary: {e}")


# ═══════════════════════════════════════════════════════════════
# FRONTEND ROUTES (Serve HTML Pages)
# ═══════════════════════════════════════════════════════════════

@app.route('/')
def index():
    """Landing page."""
    return render_template('index.html')


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
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')


@app.route('/upload')
def upload_page():
    """Resume upload & analysis page (requires login)."""
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    return render_template('upload.html')


@app.route('/data/<path:filename>')
def serve_data(filename):
    """Serve JSON files from data folder."""
    from flask import send_from_directory
    return send_from_directory('data', filename)


# ═══════════════════════════════════════════════════════════════
# AUTHENTICATION API ROUTES
# ═══════════════════════════════════════════════════════════════

@app.route('/api/signup', methods=['POST'])
def api_signup():
    """Handle user registration."""
    data = request.get_json()
    
    name     = data.get('name', '').strip()
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    # Validation
    if not name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400
    
    # Create user
    user = create_user(name, email, password)
    
    if user is None:
        return jsonify({'error': 'Email already exists'}), 409
    
    # Auto-login after signup
    session['user_id']   = user['id']
    session['user_name'] = user['name']
    session['user_email'] = user['email']
    
    return jsonify({
        'success': True,
        'message': 'Account created successfully',
        'user': {
            'id':    user['id'],
            'name':  user['name'],
            'email': user['email']
        }
    }), 201


@app.route('/api/login', methods=['POST'])
def api_login():
    """Handle user login."""
    data = request.get_json()
    
    email    = data.get('email', '').strip().lower()
    password = data.get('password', '').strip()
    
    # Validation
    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Authenticate
    user = authenticate_user(email, password)
    
    if user is None:
        return jsonify({'error': 'Invalid email or password'}), 401
    
    # Set session
    session['user_id']    = user['id']
    session['user_name']  = user['name']
    session['user_email'] = user['email']
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': {
            'id':    user['id'],
            'name':  user['name'],
            'email': user['email']
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


# ═══════════════════════════════════════════════════════════════
# RESUME UPLOAD & MANAGEMENT
# ═══════════════════════════════════════════════════════════════

@app.route('/api/upload-resume', methods=['POST'])
@login_required
def api_upload_resume():
    """Upload and save user's resume to Cloudinary (replaces old one if exists)."""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Validate file type
    if not is_supported_format(file.filename):
        return jsonify({'error': 'Only PDF and DOCX files are accepted'}), 400
    
    user_id = session['user_id']
    
    # Delete old resume from Cloudinary
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
    
    # Save to database (this will replace existing resume due to UNIQUE constraint)
    resume = save_resume(user_id, filename, file_url, public_id)
    
    if resume is None:
        # Clean up Cloudinary if DB save failed
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


# ═══════════════════════════════════════════════════════════════
# RESUME ANALYSIS API (Protected Routes)
# ═══════════════════════════════════════════════════════════════

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

        # Extract text from downloaded file
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
    
    # Get user's uploaded resume
    resume_db = get_user_resume(user_id)

    if resume_db is None:
        return jsonify({"error": "No resume uploaded. Please upload your resume first."}), 400

    try:
        # Download resume from Cloudinary URL
        response = requests.get(resume_db['file_path'], timeout=10)

        if response.status_code != 200:
            return jsonify({"error": "Failed to download resume from Cloudinary"}), 500

        file_stream = BytesIO(response.content)

        # Extract text from downloaded file
        resume_text = extract_text_from_document(file_stream, resume_db['filename'])

    except Exception as e:
        return jsonify({"error": f"Failed to read resume: {str(e)}"}), 500

    # Get top 5 recommendations from hybrid system
    try:
        recommendations = get_top5_recommendations(resume_text)
    except Exception as e:
        return jsonify({"error": f"Prediction failed: {str(e)}"}), 500

    # Also get skills for display
    resume_skills = extract_skills(resume_text)

    return jsonify({
        "resume_skills":    sorted(resume_skills),
        "recommendations":  recommendations,
        "error":            None
    })


# ═══════════════════════════════════════════════════════════════
# RUN APP
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)