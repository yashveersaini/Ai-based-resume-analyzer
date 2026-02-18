const SUBTITLES = {
  1: 'Upload your resume and a job description to get your ATS compatibility score with intelligent skill matching.',
  2: 'Upload your resume and our ML model will predict the top 3 job roles that best match your skill profile.',
};

function switchTab(n) {
  document.getElementById('tab1').style.display    = n === 1 ? 'block' : 'none';
  document.getElementById('tab2').style.display    = n === 2 ? 'block' : 'none';
  document.getElementById('tab1Btn').classList.toggle('active', n === 1);
  document.getElementById('tab2Btn').classList.toggle('active', n === 2);
  document.getElementById('headerSubtitle').textContent = SUBTITLES[n];
}

// Upload zone wiring
const uploadZone  = document.getElementById('uploadZone');
const resumeInput = document.getElementById('resumeInput');
const fileName    = document.getElementById('fileName');

resumeInput.addEventListener('change', () => {
  if (resumeInput.files[0]) {
    fileName.textContent   = '📄 ' + resumeInput.files[0].name;
    fileName.style.display = 'block';
  }
});
uploadZone.addEventListener('dragover',  e => { e.preventDefault(); uploadZone.classList.add('drag-over'); });
uploadZone.addEventListener('dragleave', () => uploadZone.classList.remove('drag-over'));
uploadZone.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f && f.type === 'application/pdf') {
    resumeInput.files        = e.dataTransfer.files;
    fileName.textContent     = '📄 ' + f.name;
    fileName.style.display   = 'block';
  } else { showError('errorBox', 'Only PDF files are accepted.'); }
});

// Error helper
function showError(boxId, msg) {
  const box = document.getElementById(boxId);
  box.textContent = '⚠ ' + msg;
  box.classList.add('visible');
  setTimeout(() => box.classList.remove('visible'), 5000);
}

// Score ring
function setScore(score) {
  const ring  = document.getElementById('scoreRing');
  const num   = document.getElementById('scoreNum');
  const title = document.getElementById('scoreTitle');
  const desc  = document.getElementById('scoreDesc');
  const circ  = 2 * Math.PI * 54;

  ring.style.strokeDasharray  = circ;
  ring.style.strokeDashoffset = circ - (score / 100) * circ;

  let color, label, description;
  if      (score >= 75) { color='#00c896'; label='Excellent Match!';   description='Your resume is highly optimized for this role. Strong chance of passing ATS filters.'; }
  else if (score >= 50) { color='#ffd43b'; label='Good Match';         description='Your resume covers many key skills. Adding missing ones will further improve your chances.'; }
  else if (score >= 25) { color='#ff9f43'; label='Partial Match';      description='Some skill gaps exist. Consider tailoring your resume specifically for this role.'; }
  else                  { color='#ff6584'; label='Low Match';          description='Few matching skills detected. A targeted resume update is strongly recommended.'; }

  ring.style.stroke  = color;
  num.textContent    = score + '%';
  num.style.color    = color;
  title.textContent  = label;
  desc.textContent   = description;
}

// Generic chips renderer
function renderChips(containerId, skills, type) {
  const el = document.getElementById(containerId);
  if (!skills || skills.length === 0) {
    el.innerHTML = '<div class="empty-state">None found.</div>';
    return;
  }
  el.innerHTML = skills.map((s, i) =>
    `<div class="skill-chip ${type}" style="animation-delay:${i * 0.06}s">
       <span class="dot"></span>${s}
     </div>`
  ).join('');
}

// Your Resume Skills renderer
function renderYourSkills(resumeSkills, matchedSkills) {
  const container = document.getElementById('yourSkills');
  const fill      = document.getElementById('skillsSummaryFill');
  const label     = document.getElementById('skillsSummaryLabel');
  const legend    = document.getElementById('skillsLegend');

  if (!resumeSkills || resumeSkills.length === 0) {
    container.innerHTML = '<div class="empty-state">No skills detected in resume.</div>';
    fill.style.width    = '0%';
    label.textContent   = '0 skills detected';
    return;
  }

  const matchSet     = new Set(matchedSkills.map(s => s.toLowerCase()));
  const matchedCount = resumeSkills.filter(s => matchSet.has(s.toLowerCase())).length;
  const pct          = Math.round((matchedCount / resumeSkills.length) * 100);

  setTimeout(() => { fill.style.width = pct + '%'; }, 100);
  label.textContent = `${resumeSkills.length} total · ${matchedCount} match this job`;

  legend.innerHTML = `
    <span class="legend-item"><span class="legend-dot match-dot"></span>Matches JD</span>
    <span class="legend-item"><span class="legend-dot skill-dot"></span>Other skills</span>`;

  // Sort: matched first
  const sorted = [
    ...resumeSkills.filter(s =>  matchSet.has(s.toLowerCase())).sort(),
    ...resumeSkills.filter(s => !matchSet.has(s.toLowerCase())).sort(),
  ];

  container.innerHTML = sorted.map((skill, i) => {
    const isMatched = matchSet.has(skill.toLowerCase());
    return `<div class="skill-chip ${isMatched ? 'your-match' : 'your-skill'}"
      style="animation-delay:${i * 0.05}s"
      title="${isMatched ? '✓ Required by this job' : 'Not required by this job'}">
      <span class="dot"></span>${skill}
    </div>`;
  }).join('');
}

// Main analyze call
async function analyzeResume() {
  const file = resumeInput.files[0];
  const jd   = document.getElementById('jobDesc').value.trim();
  const btn  = document.getElementById('analyzeBtn');

  document.getElementById('results').classList.remove('visible');
  document.getElementById('errorBox').classList.remove('visible');

  if (!file) { showError('errorBox', 'Please upload your resume PDF.'); return; }
  if (!jd)   { showError('errorBox', 'Please paste a job description.'); return; }

  btn.disabled = true;
  document.getElementById('loader').classList.add('active');

  const fd = new FormData();
  fd.append('resume', file);
  fd.append('job_description', jd);

  try {
    const res  = await fetch('/analyze', { method: 'POST', body: fd });
    const data = await res.json();

    if (data.error) {
      showError('errorBox', data.error);
    } else {
      setScore(data.score);
      renderYourSkills(data.resume_skills, data.matched_skills);
      renderChips('matchedSkills', data.matched_skills, 'match');
      renderChips('missingSkills', data.missing_skills, 'missing');
      const results = document.getElementById('results');
      results.classList.add('visible');
      results.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } catch (err) {
    showError('errorBox', 'Server error. Please make sure Flask is running.');
    console.error(err);
  } finally {
    btn.disabled = false;
    document.getElementById('loader').classList.remove('active');
  }
}


// ─────────────────────────────────────────────
// FEATURE 2 — JOB SUGGEST
// ─────────────────────────────────────────────

// Upload zone 2 wiring
const uploadZone2  = document.getElementById('uploadZone2');
const resumeInput2 = document.getElementById('resumeInput2');
const fileName2    = document.getElementById('fileName2');

resumeInput2.addEventListener('change', () => {
  if (resumeInput2.files[0]) {
    fileName2.textContent   = '📄 ' + resumeInput2.files[0].name;
    fileName2.style.display = 'block';
  }
});
uploadZone2.addEventListener('dragover',  e => { e.preventDefault(); uploadZone2.classList.add('drag-over'); });
uploadZone2.addEventListener('dragleave', () => uploadZone2.classList.remove('drag-over'));
uploadZone2.addEventListener('drop', e => {
  e.preventDefault();
  uploadZone2.classList.remove('drag-over');
  const f = e.dataTransfer.files[0];
  if (f && f.type === 'application/pdf') {
    resumeInput2.files      = e.dataTransfer.files;
    fileName2.textContent   = '📄 ' + f.name;
    fileName2.style.display = 'block';
  } else { showError('errorBox2', 'Only PDF files are accepted.'); }
});

// Rank labels
const RANK_LABELS  = ['🥇', '🥈', '🥉'];
const RANK_CLASSES = ['rank-1', 'rank-2', 'rank-3'];

// Build job role cards
function renderJobCards(suggestions) {
  const container = document.getElementById('jobCards');

  container.innerHTML = suggestions.map((job, i) => {
    // Show up to 4 matched skill mini-chips on the card
    const preview    = job.matched_skills.slice(0, 4);
    const remaining  = job.matched_skills.length - preview.length;
    const previewHtml = preview.map(s => `<span class="mini-chip">${s}</span>`).join('');
    const moreHtml    = remaining > 0 ? `<span class="mini-chip more">+${remaining} more</span>` : '';

    return `
      <div class="job-card" style="animation-delay:${i * 0.12}s">
        <div class="job-rank ${RANK_CLASSES[i]}">${RANK_LABELS[i]}</div>
        <div class="job-info">
          <div class="job-role-name">${job.role}</div>
          <div class="job-meta">
            <span class="job-confidence">${job.confidence}% match</span>
            <span class="job-skill-count">${job.matched_skills.length} / ${job.total_skills} skills matched</span>
          </div>
          <div class="job-skill-preview">${previewHtml}${moreHtml}</div>
        </div>
        <button class="btn-view" onclick="openModal(${i})">View →</button>
      </div>`;
  }).join('');
}

// Store suggestions globally for modal access
let _suggestions = [];

// Main suggest call
async function suggestJobs() {
  const file = resumeInput2.files[0];
  const btn  = document.getElementById('suggestBtn');
  const jr   = document.getElementById('jobResults');

  jr.classList.remove('visible');
  document.getElementById('errorBox2').classList.remove('visible');

  if (!file) { showError('errorBox2', 'Please upload your resume PDF.'); return; }

  btn.disabled = true;
  document.getElementById('loader2').classList.add('active');

  const fd = new FormData();
  fd.append('resume', file);

  try {
    const res  = await fetch('/suggest', { method: 'POST', body: fd });
    const data = await res.json();

    if (data.error) {
      showError('errorBox2', data.error);
    } else {
      _suggestions = data.suggestions;

      // Render detected skills
      renderChips('detectedSkills', data.resume_skills, 'your-skill');

      // Render job cards
      renderJobCards(data.suggestions);

      jr.classList.add('visible');
      jr.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  } catch (err) {
    showError('errorBox2', 'Server error. Please make sure Flask is running.');
    console.error(err);
  } finally {
    btn.disabled = false;
    document.getElementById('loader2').classList.remove('active');
  }
}


// ─────────────────────────────────────────────
// MODAL — Skills & Roadmap
// ─────────────────────────────────────────────

function openModal(index) {
  const job     = _suggestions[index];
  const overlay = document.getElementById('modalOverlay');

  // Header
  document.getElementById('modalRankBadge').textContent   = `Rank #${index + 1} Match`;
  document.getElementById('modalTitle').textContent       = job.role;
  document.getElementById('modalConfidence').textContent  =
    `${job.confidence}% confidence · ${job.matched_skills.length} of ${job.total_skills} required skills matched`;

  // Matched skills
  const skillsEl = document.getElementById('modalMatchedSkills');
  if (job.matched_skills.length === 0) {
    skillsEl.innerHTML = '<div class="no-match-state">None of your current skills match this role\'s requirements — a great learning opportunity!</div>';
  } else {
    skillsEl.innerHTML = job.matched_skills.map((s, i) =>
      `<div class="skill-chip your-match" style="animation-delay:${i * 0.05}s">
         <span class="dot"></span>${s}
       </div>`
    ).join('');
  }

  // Roadmap
  const roadmapEl = document.getElementById('modalRoadmap');
  roadmapEl.innerHTML = job.roadmap.map((step, i) =>
    `<div class="roadmap-step" style="animation-delay:${i * 0.07}s">
       <div class="step-num">${step.step}</div>
       <div class="step-body">
         <div class="step-title">${step.title}</div>
         <div class="step-desc">${step.desc}</div>
       </div>
     </div>`
  ).join('');

  overlay.classList.add('open');
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  document.getElementById('modalOverlay').classList.remove('open');
  document.body.style.overflow = '';
}

// Close on Escape key
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeModal();
});