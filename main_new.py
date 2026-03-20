"""
Streamlit UI  —  Job Role Recommender
Run:  streamlit run app_streamlit.py
"""

import streamlit as st
from utils.hybrid_recommender import get_top5_recommendations, cleanResume
from utils.document_parser import extract_text_from_pdf

st.set_page_config(page_title="Job Role Predictor", page_icon="🎯", layout="centered")

st.markdown("""
    <style>
    .card {
        background: #f8f9fa;
        border-left: 4px solid #4f8ef7;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
    }
    .card-trending { border-left-color: #22c55e; }
    .card-ml       { border-left-color: #6366f1; }
    .badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 2px 8px;
        border-radius: 12px;
        margin-left: 8px;
    }
    .badge-trending { background:#dcfce7; color:#166534; }
    .badge-ml       { background:#ede9fe; color:#4c1d95; }
    .badge-high     { background:#fef9c3; color:#854d0e; }
    .badge-medium   { background:#fee2e2; color:#991b1b; }
    .skill-pill {
        display: inline-block;
        background: #e0f2fe;
        color: #075985;
        border-radius: 6px;
        padding: 2px 8px;
        font-size: 12px;
        margin: 2px;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🎯 Job Role Recommender")
# st.caption("Paste your resume text below — get top 5 role predictions combining ML model + trending market roles.")

# resume_input = st.text_area("Resume Text", height=220,
#     placeholder="Paste your full resume or just your skills section here...")

upload_file = st.file_uploader('Upload Resume', type=['txt', 'pdf', 'docs', 'docx'])

if upload_file is not None:
    try:
        resume_input = extract_text_from_pdf(upload_file)
    except:
        st.write("Error")

if st.button("Get Recommendations", type="primary"):
    if not resume_input.strip():
        st.warning("Please paste some resume text first.")
    else:
        with st.spinner("Analysing resume..."):
            results = get_top5_recommendations(resume_input)

        st.markdown("### Top 5 Recommended Job Roles")

        for r in results:
            is_trending = r["source"] == "Trending map"
            card_cls    = "card-trending" if is_trending else "card-ml"
            badge_cls   = "badge-trending" if is_trending else "badge-ml"
            badge_txt   = "🔥 Trending" if is_trending else "📊 ML Model"
            conf        = r["confidence"]
            conf_cls    = "badge-high" if conf == "High" else "badge-medium"

            skills_html = ""
            if r["matched_skills"]:
                pills = "".join(
                    f'<span class="skill-pill">{s}</span>'
                    for s in r["matched_skills"]
                )
                skills_html = f"<div style='margin-top:6px'>{pills}</div>"

            st.markdown(f"""
            <div class="card {card_cls}">
                <div>
                    <strong>#{r['rank']} &nbsp; {r['role']}</strong>
                    <span class="badge {badge_cls}">{badge_txt}</span>
                    <span class="badge {conf_cls}">{conf} confidence</span>
                </div>
                <div style="color:#6b7280; font-size:13px; margin-top:4px;">
                    Job role: {r['role']} &nbsp;|&nbsp; Score: {r['score']:.3f}
                </div>
                {skills_html}
            </div>
            """, unsafe_allow_html=True)

        trending_count = sum(1 for r in results if r["source"] == "Trending map")
        ml_count       = 5 - trending_count
        st.caption(f"Results: {trending_count} trending map · {ml_count} ML model")

        st.write(resume_input)