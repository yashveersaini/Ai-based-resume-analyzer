// ═══════════════════════════════════════════════════════════════
// ResumeIQ — Upload Page JavaScript
// frontend/static/js/upload.js
// ═══════════════════════════════════════════════════════════════

// ── Global State ──
let currentUser = null;
let recommendations = [];
let JOB_PROFILES = {}; // Will be loaded from JSON

// ── Load Roadmaps from JSON ──
async function loadRoadmaps() {
  try {
    const response = await fetch('/data/roadmap.json');
    if (response.ok) {
      JOB_PROFILES = await response.json();
      console.log('✅ Roadmaps loaded successfully');
    } else {
      console.error('⚠ Failed to load roadmaps');
    }
  } catch (error) {
    console.error('⚠ Error loading roadmaps:', error);
  }
}

// ── Load User Info on Page Load ──
async function loadUserInfo() {
  try {
    const response = await fetch('/api/current-user');
    
    if (!response.ok) {
      window.location.href = '/login';
      return;
    }
    
    const data = await response.json();
    currentUser = data.user;
    
    document.getElementById('userName').textContent = currentUser.name;
    
    // Display current resume info
    displayResumeInfo();
    
  } catch (error) {
    console.error('Error loading user info:', error);
    window.location.href = '/login';
  }
}

function displayResumeInfo() {
  const container = document.getElementById('currentResumeInfo');
  
  if (currentUser.has_resume && currentUser.resume) {
    const uploadDate = new Date(currentUser.resume.uploaded_at).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
    
    container.innerHTML = `
      <div class="resume-info-item">
        <span class="resume-info-label">Filename:</span>
        <span class="resume-info-value">${currentUser.resume.filename}</span>
      </div>
      <div class="resume-info-item">
        <span class="resume-info-label">Uploaded:</span>
        <span class="resume-info-value">${uploadDate}</span>
      </div>
    `;
  } else {
    container.innerHTML = `
      <div class="no-resume-box">
        ⚠ No resume uploaded yet. Upload one below to get started.
      </div>
    `;
  }
}

// ── Logout ──
async function logout() {
  try {
    await fetch('/api/logout', { method: 'POST' });
    window.location.href = '/';
  } catch (error) {
    window.location.href = '/';
  }
}

// ── Tab Switching ──
function switchTab(tabName) {
  // Update tab buttons
  document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
  event.target.classList.add('active');
  
  // Update tab content
  document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
  document.getElementById(`tab-${tabName}`).classList.add('active');
}

// ══════════════════════════════════════════════════════════════
// TAB 1: RESUME UPLOAD
// ══════════════════════════════════════════════════════════════

const uploadZone = document.getElementById('uploadZone');
const resumeInput = document.getElementById('resumeInput');
const fileName = document.getElementById('fileName');
const uploadBtn = document.getElementById('uploadBtn');

// File validation
function isValidFileType(filename) {
  const validExtensions = ['.pdf', '.docx'];
  const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
  return validExtensions.includes(ext);
}

// File input change
resumeInput.addEventListener('change', () => {
  if (resumeInput.files[0]) {
    const file = resumeInput.files[0];
    if (!isValidFileType(file.name)) {
      showError('Only PDF and DOCX files are accepted');
      resumeInput.value = '';
      fileName.style.display = 'none';
      uploadBtn.disabled = true;
      return;
    }
    fileName.textContent = '📄 ' + file.name;
    fileName.style.display = 'block';
    uploadBtn.disabled = false;
  }
});

// Drag and drop
uploadZone.addEventListener('dragover', (e) => {
  e.preventDefault();
  uploadZone.classList.add('drag-over');
});

uploadZone.addEventListener('dragleave', () => {
  uploadZone.classList.remove('drag-over');
});

uploadZone.addEventListener('drop', (e) => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  
  const file = e.dataTransfer.files[0];
  if (file && isValidFileType(file.name)) {
    resumeInput.files = e.dataTransfer.files;
    fileName.textContent = '📄 ' + file.name;
    fileName.style.display = 'block';
    uploadBtn.disabled = false;
  } else {
    showError('Only PDF and DOCX files are accepted');
  }
});

// Upload resume
async function uploadResume() {
  const file = resumeInput.files[0];
  if (!file) {
    showError('Please select a file');
    return;
  }
  
  uploadBtn.disabled = true;
  uploadBtn.textContent = 'Uploading...';
  
  const formData = new FormData();
  formData.append('resume', file);
  
  try {
    const response = await fetch('/api/upload-resume', {
      method: 'POST',
      body: formData
    });
    
    const result = await response.json();
    
    if (response.ok && result.success) {
      // Reload user info to update resume status
      await loadUserInfo();
      
      // Clear file input
      resumeInput.value = '';
      fileName.style.display = 'none';
      uploadBtn.disabled = true;
      uploadBtn.textContent = 'Upload Resume';
      
      showSuccess('Resume uploaded successfully to Cloudinary!');
    } else {
      showError(result.error || 'Upload failed');
      uploadBtn.disabled = false;
      uploadBtn.textContent = 'Upload Resume';
    }
  } catch (error) {
    showError('Network error. Please try again.');
    uploadBtn.disabled = false;
    uploadBtn.textContent = 'Upload Resume';
  }
}

// ══════════════════════════════════════════════════════════════
// TAB 2: ATS SCORE ANALYSIS
// ══════════════════════════════════════════════════════════════

async function analyzeATS() {
  if (!currentUser.has_resume) {
    showError('Please upload a resume first (Upload Resume tab)');
    return;
  }
  
  const jobDesc = document.getElementById('jobDesc').value.trim();
  
  if (!jobDesc) {
    showError('Please paste a job description');
    return;
  }
  
  const loader = document.getElementById('loaderATS');
  const results = document.getElementById('atsResults');
  
  results.classList.remove('visible');
  loader.classList.add('active');
  
  const formData = new FormData();
  formData.append('job_description', jobDesc);
  
  try {
    const response = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });
    
    const data = await response.json();
    
    if (response.ok && !data.error) {
      displayATSResults(data);
      results.classList.add('visible');
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      showError(data.error || 'Analysis failed');
    }
  } catch (error) {
    showError('Network error. Please try again.');
  } finally {
    loader.classList.remove('active');
  }
}

function displayATSResults(data) {
  // Score ring
  const score = data.score;
  const ring = document.getElementById('scoreRing');
  const scoreNum = document.getElementById('scoreNum');
  const scoreTitle = document.getElementById('scoreTitle');
  const scoreDesc = document.getElementById('scoreDesc');
  
  const circumference = 2 * Math.PI * 54;
  const offset = circumference - (score / 100) * circumference;
  
  ring.style.strokeDashoffset = offset;
  scoreNum.textContent = score + '%';
  
  // Color and label based on score
  let color, label, description;
  if (score >= 75) {
    color = '#00c896';
    label = 'Excellent Match!';
    description = 'Your resume is highly optimized for this role.';
  } else if (score >= 50) {
    color = '#ff9f43';
    label = 'Good Match';
    description = 'Your resume covers many key skills.';
  } else if (score >= 25) {
    color = '#ff6584';
    label = 'Partial Match';
    description = 'Consider adding missing skills to improve your match.';
  } else {
    color = '#ff6584';
    label = 'Low Match';
    description = 'Significant skill gaps exist. Consider tailoring your resume.';
  }
  
  ring.style.stroke = color;
  scoreNum.style.color = color;
  scoreTitle.textContent = label;
  scoreDesc.textContent = description;
  
  // Matched skills
  renderSkills('matchedSkills', data.matched_skills, 'match');
  
  // Missing skills
  renderSkills('missingSkills', data.missing_skills, 'missing');
}

function renderSkills(containerId, skills, type) {
  const container = document.getElementById(containerId);
  
  if (!skills || skills.length === 0) {
    container.innerHTML = '<div class="empty-state">None found</div>';
    return;
  }
  
  container.innerHTML = skills.map(skill => 
    `<div class="skill-chip ${type}">${skill}</div>`
  ).join('');
}

// ══════════════════════════════════════════════════════════════
// TAB 3: JOB ROLE SUGGESTIONS (HYBRID RECOMMENDER)
// ══════════════════════════════════════════════════════════════

async function suggestJobs() {
  if (!currentUser.has_resume) {
    showError('Please upload a resume first (Upload Resume tab)');
    return;
  }
  
  const loader = document.getElementById('loaderSuggest');
  const results = document.getElementById('suggestResults');
  
  results.classList.remove('visible');
  loader.classList.add('active');
  
  try {
    const response = await fetch('/api/suggest', {
      method: 'POST'
    });
    
    const data = await response.json();
    
    if (response.ok && !data.error) {
      recommendations = data.recommendations;
      displaySuggestions(data);
      results.classList.add('visible');
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    } else {
      showError(data.error || 'Prediction failed');
    }
  } catch (error) {
    showError('Network error. Please try again.');
  } finally {
    loader.classList.remove('active');
  }
}

function displaySuggestions(data) {
  // Detected skills
  renderSkills('detectedSkills', data.resume_skills, 'detected');
  
  // Job cards
  const jobCards = document.getElementById('jobCards');
  const ranks = ['🥇', '🥈', '🥉', '4️⃣', '5️⃣'];
  
  jobCards.innerHTML = recommendations.map((job, i) => {
    // Display confidence with color coding
    const confClass = job.confidence === 'High' ? 'conf-high' : 
                      job.confidence === 'Medium' ? 'conf-medium' : 'conf-low';
    
    // Format score as percentage
    const scorePercent = Math.round(job.score * 100);
    
    // Source badge
    const sourceBadge = job.source === 'Trending map' 
      ? '<span class="source-badge trending">🔥 Trending</span>' 
      : '<span class="source-badge ml">🤖 ML Model</span>';
    
    return `
      <div class="job-card" onclick="openModal(${i})">
        <div class="job-rank">${ranks[i]}</div>
        <div class="job-info">
          <div class="job-role-name">${job.role}</div>
          <div class="job-meta">
            ${sourceBadge}
            <span class="job-confidence ${confClass}">${job.confidence} Confidence</span>
            <span class="job-score">${scorePercent}% Match</span>
          </div>
          ${job.matched_skills && job.matched_skills.length > 0 
            ? `<div class="matched-preview">${job.matched_skills.slice(0, 3).join(', ')}${job.matched_skills.length > 3 ? '...' : ''}</div>`
            : ''}
        </div>
      </div>
    `;
  }).join('');
}

// ══════════════════════════════════════════════════════════════
// MODAL FOR JOB DETAILS
// ══════════════════════════════════════════════════════════════

function openModal(index) {
  const job = recommendations[index];
  const overlay = document.getElementById('modalOverlay');
  
  document.getElementById('modalRankBadge').textContent = `Rank #${job.rank}`;
  document.getElementById('modalTitle').textContent = job.role;
  
  // Build confidence info
  const confInfo = `${job.confidence} Confidence · ${Math.round(job.score * 100)}% Match · Source: ${job.source}`;
  document.getElementById('modalConfidence').textContent = confInfo;
  
  // Matched skills section
  const skillsEl = document.getElementById('modalMatchedSkills');
  if (job.matched_skills && job.matched_skills.length > 0) {
    skillsEl.innerHTML = job.matched_skills.map(skill =>
      `<div class="skill-chip match">${skill}</div>`
    ).join('');
  } else {
    skillsEl.innerHTML = '<div class="empty-state">No specific skill matches available (ML-based prediction)</div>';
  }
  
  // Roadmap section - fetch from JOB_PROFILES
  const roadmapEl = document.getElementById('modalRoadmap');
  const roadmap = getRoadmapForRole(job.role);
  
  if (roadmap && roadmap.length > 0) {
    roadmapEl.innerHTML = roadmap.map(step => `
      <div class="roadmap-step">
        <div class="step-num">${step.step}</div>
        <div class="step-body">
          <div class="step-title">${step.title}</div>
          <div class="step-desc">${step.desc}</div>
        </div>
      </div>
    `).join('');
  } else {
    roadmapEl.innerHTML = `
      <div class="no-roadmap-message">
        <div class="no-roadmap-icon">📋</div>
        <div class="no-roadmap-text">Sorry, roadmap not available for this role yet.</div>
        <div class="no-roadmap-hint">We're constantly adding new career paths!</div>
      </div>
    `;
  }
  
  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

// Helper function to get roadmap from loaded profiles
function getRoadmapForRole(roleName) {
  // Return roadmap from loaded JOB_PROFILES
  return JOB_PROFILES[roleName] || null;
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

// Close modal on Escape key
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') closeModal();
});

// ══════════════════════════════════════════════════════════════
// UTILITY FUNCTIONS
// ══════════════════════════════════════════════════════════════

function showError(msg) {
  const toast = document.getElementById('errorToast');
  toast.textContent = '⚠ ' + msg;
  toast.classList.add('visible');
  setTimeout(() => toast.classList.remove('visible'), 4000);
}

function showSuccess(msg) {
  const toast = document.getElementById('errorToast');
  toast.style.background = '#00c896';
  toast.textContent = '✓ ' + msg;
  toast.classList.add('visible');
  setTimeout(() => {
    toast.classList.remove('visible');
    toast.style.background = '#ff6584';
  }, 3000);
}

// ══════════════════════════════════════════════════════════════
// INITIALIZE ON PAGE LOAD
// ══════════════════════════════════════════════════════════════

// Load roadmaps first, then user info
loadRoadmaps().then(() => {
  loadUserInfo();
});

// Check URL parameters and switch to appropriate tab
window.addEventListener('DOMContentLoaded', () => {
  const urlParams = new URLSearchParams(window.location.search);
  const tab = urlParams.get('tab');
  
  if (tab) {
    // Remove active class from all tabs
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    
    // Activate the specified tab
    if (tab === 'upload') {
      document.querySelector('.tab-btn:nth-child(1)').classList.add('active');
      document.getElementById('tab-upload').classList.add('active');
    } else if (tab === 'ats') {
      document.querySelector('.tab-btn:nth-child(2)').classList.add('active');
      document.getElementById('tab-ats').classList.add('active');
    } else if (tab === 'suggest') {
      document.querySelector('.tab-btn:nth-child(3)').classList.add('active');
      document.getElementById('tab-suggest').classList.add('active');
    }
  }
});