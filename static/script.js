// Drag & drop + file name display
const uploadZone = document.getElementById('uploadZone');
const resumeInput = document.getElementById('resumeInput');
const fileName = document.getElementById('fileName');

resumeInput.addEventListener('change', () => {
    if (resumeInput.files[0]) {
    fileName.textContent = '📄 ' + resumeInput.files[0].name;
    fileName.style.display = 'block';
    }
});

uploadZone.addEventListener('dragover', e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
    e.preventDefault();
    uploadZone.classList.remove('drag-over');
    if (e.dataTransfer.files[0]) {
    resumeInput.files = e.dataTransfer.files;
    fileName.textContent = '📄 ' + e.dataTransfer.files[0].name;
    fileName.style.display = 'block';
    }
});

function showError(msg) {
    const box = document.getElementById('errorBox');
    box.textContent = '⚠ ' + msg;
    box.classList.add('visible');
    setTimeout(() => box.classList.remove('visible'), 5000);
}

function setScore(score) {
    const ring = document.getElementById('scoreRing');
    const num = document.getElementById('scoreNum');
    const title = document.getElementById('scoreTitle');
    const desc = document.getElementById('scoreDesc');

    const circumference = 2 * Math.PI * 54; // 339.29
    const offset = circumference - (score / 100) * circumference;

    // Color based on score
    let color, label, description;
    if (score >= 75) {
    color = '#00c896'; label = 'Excellent Match!';
    description = 'Your resume is highly optimized for this job description. You have a strong chance of passing ATS filters.';
    } else if (score >= 50) {
    color = '#ffd43b'; label = 'Good Match';
    description = 'Your resume covers many key skills. Consider adding the missing skills to improve your chances.';
    } else if (score >= 25) {
    color = '#ff9f43'; label = 'Partial Match';
    description = 'Your resume matches some requirements. Significant skill gaps exist — consider tailoring your resume.';
    } else {
    color = '#ff6584'; label = 'Low Match';
    description = 'Your resume has few matching skills for this role. A targeted update is strongly recommended.';
    }

    ring.style.strokeDasharray = circumference;
    ring.style.strokeDashoffset = offset;
    ring.style.stroke = color;
    num.textContent = score + '%';
    num.style.color = color;
    title.textContent = label;
    desc.textContent = description;
}

function renderChips(containerId, skills, type) {
    const container = document.getElementById(containerId);
    if (!skills || skills.length === 0) {
    container.innerHTML = '<div class="empty-state">None found.</div>';
    return;
    }
    container.innerHTML = skills.map((s, i) =>
    `<div class="skill-chip ${type}" style="animation-delay:${i * 0.06}s">
        <span class="dot"></span>${s}
    </div>`
    ).join('');
}

async function analyzeResume() {
    const file = resumeInput.files[0];
    const jd = document.getElementById('jobDesc').value.trim();
    const btn = document.getElementById('analyzeBtn');
    const loader = document.getElementById('loader');
    const results = document.getElementById('results');

    // Clear
    results.classList.remove('visible');
    document.getElementById('errorBox').classList.remove('visible');

    if (!file) return showError('Please upload your resume PDF.');
    if (!jd) return showError('Please paste a job description.');

    btn.disabled = true;
    loader.classList.add('active');

    const formData = new FormData();
    formData.append('resume', file);
    formData.append('job_description', jd);

    try {
    const resp = await fetch('/analyze', { method: 'POST', body: formData });
    const data = await resp.json();

    if (data.error) {
        showError(data.error);
    } else {
        setScore(data.score);
        renderChips('matchedSkills', data.matched_skills, 'match');
        renderChips('missingSkills', data.missing_skills, 'missing');
        results.classList.add('visible');
        results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    } catch (err) {
    showError('Server error. Make sure Flask is running.');
    } finally {
    btn.disabled = false;
    loader.classList.remove('active');
    }
}