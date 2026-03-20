// ═══════════════════════════════════════════════════════════════
// ResumeIQ — Upload Page JavaScript
// frontend/static/js/upload.js
// ═══════════════════════════════════════════════════════════════

// ── Global State ──
let currentUser = null;
let recommendations = [];

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

// Helper function to get roadmap from predefined profiles
function getRoadmapForRole(roleName) {
  // This maps to the JOB_PROFILES from your original job_suggester.py
  const JOB_PROFILES = {
    "Data Scientist": [
      {"step": 1, "title": "Programming Foundation", "desc": "Master Python (NumPy, Pandas, Matplotlib). Learn R basics."},
      {"step": 2, "title": "Mathematics & Statistics", "desc": "Linear algebra, probability, statistics, hypothesis testing, A/B testing."},
      {"step": 3, "title": "Machine Learning", "desc": "Supervised & unsupervised learning with scikit-learn. Master regression, classification, clustering."},
      {"step": 4, "title": "Deep Learning", "desc": "Neural networks, CNNs, RNNs with TensorFlow/PyTorch. Study Transformers."},
      {"step": 5, "title": "NLP & Computer Vision", "desc": "Text processing with spaCy/NLTK, BERT fine-tuning, image classification."},
      {"step": 6, "title": "Data Engineering", "desc": "SQL, ETL pipelines, cloud storage (AWS S3, BigQuery). Learn dbt."},
      {"step": 7, "title": "Model Deployment", "desc": "REST APIs with FastAPI/Flask, Docker containers, MLflow experiment tracking."},
      {"step": 8, "title": "Portfolio & Kaggle", "desc": "Build 3–5 end-to-end projects. Compete on Kaggle. Publish on GitHub."}
    ],
    "Web Developer": [
      {"step": 1, "title": "HTML & CSS Fundamentals", "desc": "Semantic HTML5, CSS3, Flexbox, Grid, responsive design, accessibility."},
      {"step": 2, "title": "JavaScript Mastery", "desc": "ES6+, DOM, async/await, fetch API, modules, TypeScript basics."},
      {"step": 3, "title": "Frontend Framework", "desc": "Pick React or Vue or Angular. Learn state management (Redux/Pinia/NgRx)."},
      {"step": 4, "title": "Backend Development", "desc": "Node.js + Express, RESTful APIs, authentication (JWT, OAuth)."},
      {"step": 5, "title": "Databases", "desc": "SQL (PostgreSQL/MySQL) and NoSQL (MongoDB). Learn ORM (Prisma/Sequelize)."},
      {"step": 6, "title": "DevOps Basics", "desc": "Git/GitHub, CI/CD pipelines, Docker basics, Vercel/Netlify deployment."},
      {"step": 7, "title": "Performance & Security", "desc": "Web vitals, lazy loading, HTTPS, CORS, XSS/CSRF prevention, CSP headers."},
      {"step": 8, "title": "Build Projects", "desc": "Ship 3 full-stack projects. Contribute to open source. Build your portfolio site."}
    ],
    "DevOps Engineer": [
      {"step": 1, "title": "Linux & Scripting", "desc": "Linux administration, bash scripting, cron jobs, file systems, networking."},
      {"step": 2, "title": "Version Control & CI/CD", "desc": "Git mastery, GitHub Actions, GitLab CI, Jenkins pipelines."},
      {"step": 3, "title": "Containers", "desc": "Docker (build, run, compose). Understand container registries and security."},
      {"step": 4, "title": "Container Orchestration", "desc": "Kubernetes (pods, services, deployments, Helm charts, namespaces)."},
      {"step": 5, "title": "Infrastructure as Code", "desc": "Terraform for provisioning, Ansible for configuration management."},
      {"step": 6, "title": "Cloud Platforms", "desc": "AWS (EC2, S3, EKS, RDS, IAM) or Azure/GCP equivalents. Get certified."},
      {"step": 7, "title": "Monitoring & Observability", "desc": "Prometheus, Grafana, ELK stack, alerting, log aggregation, tracing."},
      {"step": 8, "title": "Security & Compliance", "desc": "DevSecOps, secret management (Vault), SAST/DAST, network security."}
    ],
    "Data Analyst": [
      {"step": 1, "title": "Excel Mastery", "desc": "VLOOKUP, pivot tables, power query, charts. Excel is the foundation."},
      {"step": 2, "title": "SQL", "desc": "SELECT, JOINs, GROUP BY, subqueries, window functions, CTEs."},
      {"step": 3, "title": "Data Visualization", "desc": "Tableau or Power BI (DAX). Design dashboards that tell a story."},
      {"step": 4, "title": "Python for Analytics", "desc": "Pandas for data wrangling, Matplotlib/Seaborn for charts, Jupyter notebooks."},
      {"step": 5, "title": "Statistics", "desc": "Descriptive stats, distributions, hypothesis testing, regression basics."},
      {"step": 6, "title": "Business Acumen", "desc": "KPIs, cohort analysis, funnel analysis, A/B testing, storytelling with data."},
      {"step": 7, "title": "Cloud & Big Data Basics", "desc": "BigQuery, Snowflake, AWS Redshift basics. Learn dbt for transformations."},
      {"step": 8, "title": "Communication & Portfolio", "desc": "Present analysis clearly. Build a portfolio with real business insights."}
    ],
    "Backend Developer": [
      {"step": 1, "title": "Programming Language", "desc": "Deep-dive: Python (Django/FastAPI), Java (Spring Boot), or Node.js (Express)."},
      {"step": 2, "title": "Databases", "desc": "SQL (PostgreSQL, MySQL) + NoSQL (MongoDB, Redis). Master query optimization."},
      {"step": 3, "title": "API Design", "desc": "REST APIs (versioning, pagination, auth). GraphQL basics. OpenAPI/Swagger docs."},
      {"step": 4, "title": "Authentication & Security", "desc": "JWT, OAuth2, session management, rate limiting, input validation."},
      {"step": 5, "title": "Caching & Messaging", "desc": "Redis caching, Celery tasks, message queues (RabbitMQ/Kafka)."},
      {"step": 6, "title": "Containerization", "desc": "Docker, docker-compose. Understand multi-stage builds and secrets."},
      {"step": 7, "title": "System Design", "desc": "Scalability, load balancing, microservices architecture, distributed systems."},
      {"step": 8, "title": "Production Skills", "desc": "CI/CD, logging, monitoring, cloud deployment (AWS/GCP). Code reviews."}
    ],
    "Mobile Developer": [
      {"step": 1, "title": "Choose Your Platform", "desc": "Android (Kotlin + Jetpack Compose) or iOS (Swift + SwiftUI) or cross-platform (Flutter/React Native)."},
      {"step": 2, "title": "UI Development", "desc": "Layouts, navigation, lists, animations. Follow platform design guidelines (Material/HIG)."},
      {"step": 3, "title": "State Management", "desc": "MVVM, BLoC, Redux, Provider. Understand reactive programming."},
      {"step": 4, "title": "Networking", "desc": "REST APIs with Retrofit/Alamofire/Axios. JSON parsing. Error handling."},
      {"step": 5, "title": "Local Storage", "desc": "Room (Android), Core Data (iOS), SQLite, SharedPreferences/UserDefaults."},
      {"step": 6, "title": "Firebase & Backend", "desc": "Firebase Auth, Firestore, FCM push notifications, Analytics."},
      {"step": 7, "title": "Testing & Publishing", "desc": "Unit tests, UI tests. Publish to Play Store & App Store. CI/CD with Fastlane."},
      {"step": 8, "title": "Advanced Topics", "desc": "Offline-first architecture, performance optimization, accessibility, deep links."}
    ],
    "Cybersecurity Analyst": [
      {"step": 1, "title": "Networking Fundamentals", "desc": "TCP/IP, DNS, HTTP, firewalls, VPNs. Use Wireshark to analyze traffic."},
      {"step": 2, "title": "Linux Mastery", "desc": "Linux command line, file permissions, processes, Bash scripting. Use Kali Linux."},
      {"step": 3, "title": "Ethical Hacking Basics", "desc": "OWASP Top 10, Nmap, Metasploit, Burp Suite. Practice on HackTheBox/TryHackMe."},
      {"step": 4, "title": "Security Operations", "desc": "SOC workflows, SIEM (Splunk/QRadar), log analysis, alert triage."},
      {"step": 5, "title": "Penetration Testing", "desc": "Web app, network, and mobile pentesting. Reporting vulnerabilities professionally."},
      {"step": 6, "title": "Incident Response", "desc": "Digital forensics, memory analysis, malware triage, IR playbooks."},
      {"step": 7, "title": "Cloud Security", "desc": "AWS/Azure IAM, zero trust, CSPM tools. Understand cloud threat models."},
      {"step": 8, "title": "Certifications", "desc": "Pursue CompTIA Security+, CEH, OSCP, CISSP. Build a home lab."}
    ],
    "Cloud Engineer": [
      {"step": 1, "title": "Cloud Fundamentals", "desc": "Understand IaaS/PaaS/SaaS. Pick AWS or Azure or GCP. Get free tier account."},
      {"step": 2, "title": "Core Services", "desc": "Compute (EC2/VMs), Storage (S3/Blob), Networking (VPC/VNet), IAM/RBAC."},
      {"step": 3, "title": "Infrastructure as Code", "desc": "Terraform for multi-cloud provisioning. Learn modules and state management."},
      {"step": 4, "title": "Containers & Orchestration", "desc": "Docker + Kubernetes (EKS/AKS/GKE). Helm charts, namespaces, autoscaling."},
      {"step": 5, "title": "Serverless", "desc": "AWS Lambda, Azure Functions, Cloud Run. Event-driven architectures."},
      {"step": 6, "title": "Networking & Security", "desc": "VPCs, subnets, security groups, WAF, load balancers, CDN, DNS."},
      {"step": 7, "title": "Monitoring & Cost", "desc": "CloudWatch/Azure Monitor, cost optimization (Reserved Instances, spot), FinOps."},
      {"step": 8, "title": "Certifications", "desc": "AWS Solutions Architect / Azure Administrator / GCP ACE. Then specializations."}
    ],
    "ML Engineer": [
      {"step": 1, "title": "ML Foundations", "desc": "Python, scikit-learn, pandas, statistics, model evaluation. Understand the full ML lifecycle."},
      {"step": 2, "title": "Deep Learning", "desc": "TensorFlow or PyTorch. CNNs, RNNs, Transformers, fine-tuning pre-trained models."},
      {"step": 3, "title": "Data Pipelines", "desc": "Apache Airflow, Spark/PySpark, feature stores (Feast). ETL at scale."},
      {"step": 4, "title": "Model Serving", "desc": "REST APIs (FastAPI/Flask), TF Serving, Triton Inference Server, ONNX."},
      {"step": 5, "title": "MLOps Tooling", "desc": "MLflow (tracking, registry), DVC, Weights & Biases, experiment management."},
      {"step": 6, "title": "Containerization & Orchestration", "desc": "Docker, Kubernetes, Kubeflow. Scalable model training and deployment."},
      {"step": 7, "title": "Cloud ML Platforms", "desc": "AWS SageMaker, GCP Vertex AI, Azure ML. Managed training and deployment."},
      {"step": 8, "title": "LLMs & Advanced Topics", "desc": "Fine-tuning LLMs, RAG pipelines, vector databases, prompt engineering."}
    ],
    "Database Administrator": [
      {"step": 1, "title": "SQL Mastery", "desc": "Advanced SQL: window functions, CTEs, stored procedures, triggers, indexes."},
      {"step": 2, "title": "Database Internals", "desc": "Storage engines, query planners, execution plans, ACID properties, transactions."},
      {"step": 3, "title": "Performance Tuning", "desc": "Index optimization, query rewriting, EXPLAIN ANALYZE, caching, connection pooling."},
      {"step": 4, "title": "Backup & Recovery", "desc": "Full/incremental backups, point-in-time recovery, RTO/RPO planning, testing restores."},
      {"step": 5, "title": "Replication & HA", "desc": "Primary-replica setup, failover, load balancing (pgBouncer, ProxySQL)."},
      {"step": 6, "title": "NoSQL Databases", "desc": "MongoDB, Redis, Cassandra. Understand CAP theorem and when to use NoSQL."},
      {"step": 7, "title": "Cloud Databases", "desc": "AWS RDS/Aurora, Azure SQL, GCP Cloud SQL, Snowflake, BigQuery."},
      {"step": 8, "title": "Security & Compliance", "desc": "Encryption at rest/transit, auditing, RBAC, GDPR/HIPAA compliance, data masking."}
    ]
  };
  
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

loadUserInfo();

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