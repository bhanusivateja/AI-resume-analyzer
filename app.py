"""
app.py - AI Resume Analyzer & Intelligent ATS Career Assistant
Main Streamlit Application with Dark Navy Theme, Interactive Gauges,
Explainable Scoring, Bullet Enhancer, SQLite History, and PDF/CSV Export.
"""

import os
import json
import io
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# Import custom core modules
from modules.resume_parser import ResumeParser, ResumeParsingError
from modules.skill_extractor import SkillExtractor
from modules.job_matcher import JobMatcher
from modules.ats_scorer import ATSScorer
from modules.recommendations import RecommendationEngine, ResumeImprovementAssistant
from modules.report_generator import ReportGenerator
from modules.database import DatabaseManager

# Page Configuration
st.set_page_config(
    page_title="AI Resume Analyzer – Intelligent ATS & Career Assistant",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load CSS Styles
CSS_PATH = os.path.join(os.path.dirname(__file__), "assets", "style.css")
if os.path.exists(CSS_PATH):
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Initialize Session State
if "resume_data" not in st.session_state:
    st.session_state.resume_data = None
if "jd_text" not in st.session_state:
    st.session_state.jd_text = ""
if "job_title" not in st.session_state:
    st.session_state.job_title = "AI / ML Engineer"
if "match_results" not in st.session_state:
    st.session_state.match_results = None
if "ats_results" not in st.session_state:
    st.session_state.ats_results = None
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "custom_skills" not in st.session_state:
    st.session_state.custom_skills = []
if "sample_resume_loaded" not in st.session_state:
    st.session_state.sample_resume_loaded = None

# Singletons / Core Services
@st.cache_resource
def get_services():
    parser = ResumeParser()
    skill_extractor = SkillExtractor()
    job_matcher = JobMatcher(skill_extractor)
    scorer = ATSScorer()
    rec_engine = RecommendationEngine()
    bullet_assistant = ResumeImprovementAssistant()
    report_gen = ReportGenerator()
    db = DatabaseManager()
    return parser, skill_extractor, job_matcher, scorer, rec_engine, bullet_assistant, report_gen, db

parser, skill_extractor, job_matcher, scorer, rec_engine, bullet_assistant, report_gen, db = get_services()

# Load Sample Jobs
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")
SAMPLE_JOBS_PATH = os.path.join(SAMPLES_DIR, "sample_jobs.json")
sample_jobs = {}
if os.path.exists(SAMPLE_JOBS_PATH):
    try:
        with open(SAMPLE_JOBS_PATH, "r", encoding="utf-8") as f:
            sample_jobs = json.load(f)
    except Exception:
        sample_jobs = {}


# Visualization Helpers
def render_gauge_chart(score: float, rating: dict) -> go.Figure:
    """Render modern circular gauge with dark styling."""
    color = rating.get("color", "#6366F1")
    label = rating.get("label", "Estimated Fit")

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': f"<b>ATS Compatibility</b><br><span style='font-size:14px;color:{color}'>{label}</span>", 'font': {'size': 18, 'color': '#F3F4F6'}},
        number={'suffix': "/100", 'font': {'size': 38, 'color': '#FFFFFF', 'family': 'sans-serif'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': "#94A3B8"}},
            'bar': {'color': color, 'thickness': 0.28},
            'bgcolor': "rgba(30, 41, 59, 0.4)",
            'borderwidth': 1,
            'bordercolor': "rgba(255, 255, 255, 0.1)",
            'steps': [
                {'range': [0, 40], 'color': "rgba(239, 68, 68, 0.15)"},
                {'range': [40, 60], 'color': "rgba(245, 158, 11, 0.15)"},
                {'range': [60, 80], 'color': "rgba(59, 130, 246, 0.15)"},
                {'range': [80, 100], 'color': "rgba(16, 185, 129, 0.15)"}
            ],
            'threshold': {
                'line': {'color': "#FFFFFF", 'width': 3},
                'thickness': 0.8,
                'value': score
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=25, r=25, t=50, b=20),
        height=260
    )
    return fig


def render_breakdown_bar_chart(breakdown: dict) -> go.Figure:
    """Render horizontal bar chart for the 4 scoring pillars."""
    categories = [v["name"] for v in breakdown.values()]
    raw_scores = [v["raw_score"] for v in breakdown.values()]
    weighted_scores = [v["weighted_score"] for v in breakdown.values()]
    weights = [f"Weight: {v['weight']}%" for v in breakdown.values()]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=categories,
        x=raw_scores,
        orientation='h',
        name='Raw Score (%)',
        marker=dict(color='#6366F1', opacity=0.85, line=dict(color='#818CF8', width=1)),
        text=[f"{s}%" for s in raw_scores],
        textposition='auto',
        hoverinfo='text+name',
        hovertext=[f"{cat}: {s}% ({w})" for cat, s, w in zip(categories, raw_scores, weights)]
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(range=[0, 100], gridcolor='rgba(255,255,255,0.08)', tickfont=dict(color='#94A3B8')),
        yaxis=dict(tickfont=dict(color='#E2E8F0', size=12), autorange="reversed"),
        margin=dict(l=10, r=20, t=20, b=20),
        height=220,
        showlegend=False
    )
    return fig


# Sidebar Navigation
with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 12px 0 20px 0;">
            <div style="font-size: 32px; margin-bottom: 6px;">🎯</div>
            <h2 style="margin: 0; font-size: 20px; font-weight: 700; color: #FFFFFF;">AI Resume Analyzer</h2>
            <p style="margin: 0; font-size: 12px; color: #818CF8; letter-spacing: 0.05em;">Intelligent ATS & Career Assistant</p>
        </div>
    """, unsafe_allow_html=True)

    page = st.radio(
        "Navigation",
        [
            "🏠 Home / Dashboard",
            "🔍 Analyze Resume",
            "📊 Skills Gap Analysis",
            "✍️ Resume Improvement Assistant",
            "📜 Analysis History",
            "ℹ️ About Project"
        ],
        index=0
    )

    st.markdown("---")
    st.markdown("""
        <div style="background: rgba(15, 23, 42, 0.6); padding: 12px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.06); font-size: 11.5px; color: #94A3B8;">
            <b style="color: #F1F5F9;">Academic Project:</b> CSE (AI & ML)<br/>
            <b>Version:</b> 1.0.0 (Local Offline Mode)<br/>
            <b>Core Engine:</b> Scikit-learn, TF-IDF, ReportLab, SQLite
        </div>
    """, unsafe_allow_html=True)


# PAGE 1: HOME / DASHBOARD
if page == "🏠 Home / Dashboard":
    st.markdown("""
        <div class="hero-banner">
            <h1 style="margin: 0 0 10px 0; font-size: 30px; font-weight: 800; color: #FFFFFF;">
                Optimize Your Resume for Modern ATS Algorithms 🚀
            </h1>
            <p style="margin: 0 0 20px 0; font-size: 15px; color: #CBD5E1; line-height: 1.6; max-width: 820px;">
                Upload your PDF resume, compare it against target job descriptions with transparent TF-IDF similarity,
                uncover critical skill gaps, and transform weak bullet points into high-impact accomplishments.
            </p>
            <div style="display: flex; gap: 12px; flex-wrap: wrap;">
                <span class="skill-tag skill-tag-matched">✓ 100% Free & Local</span>
                <span class="skill-tag skill-tag-extra">⚡ Transparent Scoring</span>
                <span class="skill-tag skill-tag-matched">📄 PDF & CSV Reports</span>
                <span class="skill-tag skill-tag-extra">🔒 Privacy-First (No Cloud PII)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Summary Stats from Database
    analyses = db.get_all_analyses()
    total_scans = len(analyses)
    avg_score = round(sum(a["overall_score"] for a in analyses) / total_scans, 1) if total_scans > 0 else 0.0
    high_score = round(max((a["overall_score"] for a in analyses), default=0.0), 1)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{total_scans}</div>
                <div class="metric-label">Total Resumes Scanned</div>
            </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{avg_score}%</div>
                <div class="metric-label">Average Match Score</div>
            </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{high_score}%</div>
                <div class="metric-label">Top Recorded Score</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown("""
            <div class="metric-card">
                <div class="metric-value">4 Pillars</div>
                <div class="metric-label">Explainable Scoring Model</div>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.subheader("How It Works")

    step_cols = st.columns(4)
    with step_cols[0]:
        st.markdown("""
            <div class="dashboard-card" style="height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">📤</div>
                <h4 style="margin: 0 0 6px 0; color: #FFFFFF;">1. PDF Extraction</h4>
                <p style="font-size: 13px; color: #94A3B8; line-height: 1.5;">
                    Extracts structured text, candidate contact channels, education, projects, and work history using pdfminer.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with step_cols[1]:
        st.markdown("""
            <div class="dashboard-card" style="height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">🧠</div>
                <h4 style="margin: 0 0 6px 0; color: #FFFFFF;">2. NLP & Skill Mapping</h4>
                <p style="font-size: 13px; color: #94A3B8; line-height: 1.5;">
                    Scans 150+ technical and soft skills with robust alias resolution, n-grams, and special symbol support (C++, K8s).
                </p>
            </div>
        """, unsafe_allow_html=True)
    with step_cols[2]:
        st.markdown("""
            <div class="dashboard-card" style="height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">⚖️</div>
                <h4 style="margin: 0 0 6px 0; color: #FFFFFF;">3. Transparent Scoring</h4>
                <p style="font-size: 13px; color: #94A3B8; line-height: 1.5;">
                    Calculates a normalized 0-100 compatibility score across Skill Coverage, TF-IDF Cosine Similarity, Projects, and Education.
                </p>
            </div>
        """, unsafe_allow_html=True)
    with step_cols[3]:
        st.markdown("""
            <div class="dashboard-card" style="height: 100%;">
                <div style="font-size: 26px; margin-bottom: 8px;">✨</div>
                <h4 style="margin: 0 0 6px 0; color: #FFFFFF;">4. Actionable Polish</h4>
                <p style="font-size: 13px; color: #94A3B8; line-height: 1.5;">
                    Provides priority checklists, flags vague expressions, and optimizes bullets using the STAR XYZ formula.
                </p>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.info("💡 **Ready to test?** Navigate to **Analyze Resume** in the sidebar to upload a resume or test with 1-click synthetic samples!")


# PAGE 2: ANALYZE RESUME
elif page == "🔍 Analyze Resume":
    st.title("Resume & Job Description Analysis")
    st.caption("Upload your resume in PDF format and compare it against any target job description.")

    # Two Main Columns for Inputs
    col_resume, col_jd = st.columns(2)

    with col_resume:
        st.subheader("1. Resume Source (PDF)")
        uploaded_file = st.file_uploader("Upload PDF Resume", type=["pdf"], help="Upload PDF up to 10MB")

        # Quick Synthetic Sample Buttons
        st.markdown("<p style='font-size: 12px; color: #94A3B8; margin-bottom: 6px;'>Or load a synthetic sample resume:</p>", unsafe_allow_html=True)
        s_btn_c1, s_btn_c2 = st.columns(2)
        with s_btn_c1:
            if st.button("🤖 Sample AI/ML Resume", use_container_width=True):
                path = os.path.join(SAMPLES_DIR, "sample_resume_aiml.pdf")
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        content = f.read()
                    parsed = parser.parse(content, "sample_resume_aiml.pdf")
                    st.session_state.resume_data = parsed
                    st.session_state.custom_skills = skill_extractor.extract_skills_from_text(parsed["cleaned_text"])["skills"]
                    st.session_state.sample_resume_loaded = "AI / ML Engineer"
                    st.success("Loaded synthetic AI/ML sample resume!")
        with s_btn_c2:
            if st.button("💻 Sample Full Stack Resume", use_container_width=True):
                path = os.path.join(SAMPLES_DIR, "sample_resume_swe.pdf")
                if os.path.exists(path):
                    with open(path, "rb") as f:
                        content = f.read()
                    parsed = parser.parse(content, "sample_resume_swe.pdf")
                    st.session_state.resume_data = parsed
                    st.session_state.custom_skills = skill_extractor.extract_skills_from_text(parsed["cleaned_text"])["skills"]
                    st.session_state.sample_resume_loaded = "Full Stack Engineer"
                    st.success("Loaded synthetic Full Stack sample resume!")

        # Process user uploaded file
        if uploaded_file is not None:
            try:
                content = uploaded_file.read()
                parsed = parser.parse(content, uploaded_file.name)
                st.session_state.resume_data = parsed
                st.session_state.custom_skills = skill_extractor.extract_skills_from_text(parsed["cleaned_text"])["skills"]
                st.session_state.sample_resume_loaded = uploaded_file.name
                st.success(f"Parsed `{uploaded_file.name}` successfully!")
            except ResumeParsingError as e:
                st.error(f"Resume Parsing Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error: {str(e)}")

        # Display Resume Summary if parsed
        if st.session_state.resume_data:
            res = st.session_state.resume_data
            contacts = res.get("contact_info", {})
            meta = res.get("metadata", {})

            st.markdown(f"""
                <div class="dashboard-card" style="margin-top: 14px;">
                    <div style="font-weight: 700; color: #FFFFFF; font-size: 16px;">
                        👤 {contacts.get('name') or 'Candidate Profile'}
                    </div>
                    <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
                        📧 {contacts.get('email') or 'No email detected'} &nbsp;|&nbsp; 
                        📞 {contacts.get('phone') or 'No phone detected'}
                    </div>
                    <div style="font-size: 12px; color: #818CF8; margin-top: 4px;">
                        Pages: {meta.get('page_count')} | Words: {meta.get('word_count')} | Est. Reading Time: {meta.get('reading_time_minutes')} min
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with st.expander("📄 View Extracted Resume Text & Sections"):
                sec_tabs = st.tabs(["Raw Text", "Summary", "Skills", "Experience", "Projects", "Education"])
                with sec_tabs[0]:
                    st.text_area("Full Extracted Text", res["cleaned_text"], height=200, disabled=True)
                with sec_tabs[1]:
                    st.write(res["sections"].get("summary") or "Not detected")
                with sec_tabs[2]:
                    st.write(res["sections"].get("skills") or "Not detected")
                with sec_tabs[3]:
                    st.write(res["sections"].get("experience") or "Not detected")
                with sec_tabs[4]:
                    st.write(res["sections"].get("projects") or "Not detected")
                with sec_tabs[5]:
                    st.write(res["sections"].get("education") or "Not detected")

            # Allow user to inspect and edit extracted skills
            st.markdown("<p style='font-size: 13px; font-weight: 600; color: #E2E8F0; margin-top: 10px;'>Verify / Edit Detected Skills:</p>", unsafe_allow_html=True)
            all_known = sorted(list(skill_extractor.all_skills))
            edited_skills = st.multiselect(
                "Detected Skills (You can add or remove detected skills)",
                options=all_known,
                default=[s for s in st.session_state.custom_skills if s in all_known],
                help="Automated extraction can miss abbreviations or misread styling. Adjust as needed."
            )
            st.session_state.custom_skills = edited_skills

    with col_jd:
        st.subheader("2. Target Job Description")

        # Preset Job Selection
        preset_options = ["Custom (Paste your own)"] + list(sample_jobs.keys())
        selected_preset = st.selectbox("Load Sample Job Description", preset_options, index=1 if sample_jobs else 0)

        target_title = st.text_input("Target Job Title", value=selected_preset if selected_preset != "Custom (Paste your own)" else "Software Engineer")
        st.session_state.job_title = target_title

        default_jd_text = ""
        if selected_preset in sample_jobs:
            default_jd_text = sample_jobs[selected_preset]

        jd_input = st.text_area(
            "Paste Job Description Here",
            value=default_jd_text,
            height=280,
            placeholder="Paste complete job requirements, qualifications, and responsibilities..."
        )
        st.session_state.jd_text = jd_input

        # Advanced Weights Expander
        with st.expander("⚙️ Customize ATS Scoring Weights"):
            st.caption("Adjust weight distribution between scoring pillars (must sum to 100%).")
            w_skills = st.slider("Skill Coverage Weight (%)", 10, 60, 40)
            w_sim = st.slider("Semantic Text Similarity Weight (%)", 10, 50, 25)
            w_exp = st.slider("Experience & Projects Weight (%)", 10, 40, 20)
            w_edu = st.slider("Education Weight (%)", 5, 30, 15)

            total_w = w_skills + w_sim + w_exp + w_edu
            if total_w != 100:
                st.warning(f"Weights sum to {total_w}%. They will be automatically normalized to 100%.")

    # Match Action Button
    st.markdown("---")
    run_btn = st.button("🚀 Run Intelligent ATS Analysis", type="primary", use_container_width=True)

    if run_btn:
        if not st.session_state.resume_data:
            st.error("Please upload a PDF resume or select a sample resume first.")
        elif not jd_input.strip():
            st.error("Please paste or select a Job Description before running the analysis.")
        else:
            with st.spinner("Analyzing resume semantics, skill overlap, and ATS compatibility..."):
                # 1. Matching
                resume_text = st.session_state.resume_data["cleaned_text"]
                custom_skills = st.session_state.custom_skills
                match_results = job_matcher.match(
                    resume_text=resume_text,
                    jd_text=jd_input,
                    resume_skills_override=custom_skills if custom_skills else None
                )
                st.session_state.match_results = match_results

                # 2. Scoring with weights
                custom_weights_dict = {
                    "skill_coverage": w_skills / 100.0,
                    "text_similarity": w_sim / 100.0,
                    "experience_projects": w_exp / 100.0,
                    "education": w_edu / 100.0
                }
                custom_scorer = ATSScorer(custom_weights_dict)
                ats_results = custom_scorer.calculate_score(
                    match_results,
                    st.session_state.resume_data["sections"]
                )
                st.session_state.ats_results = ats_results

                # 3. Recommendations
                recs = rec_engine.generate_recommendations(
                    match_results,
                    ats_results,
                    st.session_state.resume_data
                )
                st.session_state.recommendations = recs

                # 4. Save to SQLite History
                cand_name = st.session_state.resume_data["contact_info"].get("name") or "Candidate"
                db.save_analysis(
                    candidate_name=cand_name,
                    job_title=target_title,
                    overall_score=ats_results["overall_score"],
                    rating_label=ats_results["rating"]["label"],
                    matched_skills=match_results["matched_skills"],
                    missing_skills=match_results["missing_skills"]
                )

            st.toast("Analysis complete! View audit results below.", icon="✅")

    # DISPLAY ANALYSIS RESULTS
    if st.session_state.ats_results and st.session_state.match_results:
        ats = st.session_state.ats_results
        match = st.session_state.match_results

        st.markdown("<br/>", unsafe_allow_html=True)
        st.header("ATS Compatibility Dashboard")

        # Top Metric Cards & Gauge
        g_col, m_col = st.columns([1, 1.2])

        with g_col:
            gauge_fig = render_gauge_chart(ats["overall_score"], ats["rating"])
            st.plotly_chart(gauge_fig, use_container_width=True)

        with m_col:
            st.markdown(f"""
                <div class="dashboard-card" style="height: 260px; display: flex; flex-direction: column; justify-content: center;">
                    <div style="font-size: 14px; font-weight: 700; color: #818CF8; margin-bottom: 6px;">COMPATIBILITY VERDICT</div>
                    <div style="font-size: 22px; font-weight: 700; color: {ats['rating']['color']}; margin-bottom: 8px;">
                        {ats['rating']['badge']}
                    </div>
                    <p style="font-size: 13.5px; color: #CBD5E1; line-height: 1.5; margin-bottom: 12px;">
                        {ats['rating']['summary']}
                    </p>
                    <div style="display: flex; gap: 16px; font-size: 13px; color: #94A3B8;">
                        <div><b>Skill Coverage:</b> <span style="color:#34D399;">{match['skill_coverage_pct']}%</span></div>
                        <div><b>Semantic Similarity:</b> <span style="color:#60A5FA;">{match['tfidf_similarity_pct']}%</span></div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

        # 4 Pillars Breakdown Chart & Explanation
        st.subheader("Scoring Pillar Breakdown")
        b_col1, b_col2 = st.columns([1.2, 1])
        with b_col1:
            bar_fig = render_breakdown_bar_chart(ats["breakdown"])
            st.plotly_chart(bar_fig, use_container_width=True)
        with b_col2:
            st.markdown(f"""
                <div class="dashboard-card" style="font-size: 12.5px; line-height: 1.6;">
                    <div style="font-weight: 700; color: #FFFFFF; margin-bottom: 6px;">📐 Transparent Formula</div>
                    <code style="display: block; padding: 6px; background: rgba(0,0,0,0.3); border-radius: 4px; font-size: 11px; margin-bottom: 8px; color: #A5B4FC;">
                        {ats['formula_explanation']}
                    </code>
                    <ul style="padding-left: 16px; margin: 0; color: #94A3B8;">
                        <li><b>Skill Coverage:</b> {ats['breakdown']['skill_coverage']['explanation']}</li>
                        <li><b>Text Similarity:</b> {ats['breakdown']['text_similarity']['explanation']}</li>
                        <li><b>Experience & Projects:</b> {ats['breakdown']['experience_projects']['explanation']}</li>
                        <li><b>Education:</b> {ats['breakdown']['education']['explanation']}</li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

        # Matched vs Missing Skills Tags
        st.subheader("Skill Match Analysis")
        sk_col1, sk_col2, sk_col3 = st.columns(3)

        with sk_col1:
            st.markdown(f"""
                <div class="dashboard-card">
                    <h4 style="margin: 0 0 10px 0; color: #34D399;">
                        ✅ Matched Skills ({len(match['matched_skills'])})
                    </h4>
                    <div>
            """, unsafe_allow_html=True)
            if match["matched_skills"]:
                for s in match["matched_skills"]:
                    st.markdown(f"<span class='skill-tag skill-tag-matched'>{s}</span>", unsafe_allow_html=True)
            else:
                st.caption("No overlapping skills detected.")
            st.markdown("</div></div>", unsafe_allow_html=True)

        with sk_col2:
            st.markdown(f"""
                <div class="dashboard-card">
                    <h4 style="margin: 0 0 10px 0; color: #F87171;">
                        ❌ Missing Required Skills ({len(match['missing_skills'])})
                    </h4>
                    <div>
            """, unsafe_allow_html=True)
            if match["missing_skills"]:
                for s in match["missing_skills"]:
                    st.markdown(f"<span class='skill-tag skill-tag-missing'>{s}</span>", unsafe_allow_html=True)
            else:
                st.caption("All job description skills matched!")
            st.markdown("</div></div>", unsafe_allow_html=True)

        with sk_col3:
            st.markdown(f"""
                <div class="dashboard-card">
                    <h4 style="margin: 0 0 10px 0; color: #818CF8;">
                        💡 Additional Resume Skills ({len(match['additional_skills'])})
                    </h4>
                    <div>
            """, unsafe_allow_html=True)
            if match["additional_skills"]:
                for s in match["additional_skills"][:15]:
                    st.markdown(f"<span class='skill-tag skill-tag-extra'>{s}</span>", unsafe_allow_html=True)
            else:
                st.caption("No extra skills listed.")
            st.markdown("</div></div>", unsafe_allow_html=True)

        # Prioritized Improvement Recommendations
        st.subheader("Prioritized Recommendations")
        if st.session_state.recommendations:
            for rec in st.session_state.recommendations:
                p_class = "badge-priority-high" if rec["priority"] == "High" else "badge-priority-med" if rec["priority"] == "Medium" else "badge-priority-low"
                box_class = "rec-box-high" if rec["priority"] == "High" else "rec-box-medium" if rec["priority"] == "Medium" else "rec-box-low"

                st.markdown(f"""
                    <div class="rec-box {box_class}">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                            <b style="color: #FFFFFF; font-size: 14.5px;">{rec['title']}</b>
                            <span class="{p_class}">{rec['priority']} Priority</span>
                        </div>
                        <p style="font-size: 13px; color: #94A3B8; margin-bottom: 6px;">{rec['description']}</p>
                        <div style="font-size: 12.5px; color: #A5B4FC;">
                            <b>Action Step:</b> {rec['action']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)

        # Download Reports Section
        st.subheader("Export Audit Reports")
        d_col1, d_col2 = st.columns(2)

        cand_name = st.session_state.resume_data["contact_info"].get("name") or "Candidate"
        target_role = st.session_state.job_title

        with d_col1:
            pdf_bytes = report_gen.generate_pdf_report(
                candidate_name=cand_name,
                job_title=target_role,
                ats_results=ats,
                match_results=match,
                recommendations=st.session_state.recommendations
            )
            st.download_button(
                label="📥 Download Full PDF Audit Report",
                data=pdf_bytes,
                file_name="ATS_Resume_Audit_Report.pdf",
                mime="application/pdf",
                use_container_width=True
            )

        with d_col2:
            csv_str = report_gen.generate_csv_report(
                match_results=match,
                recommendations=st.session_state.recommendations
            )
            st.download_button(
                label="📊 Download CSV Data Breakdown",
                data=csv_str,
                file_name="ATS_Skills_Breakdown.csv",
                mime="text/csv",
                use_container_width=True
            )

        # Transparent Disclaimer
        st.markdown(f"""
            <p style="font-size: 11px; color: #64748B; margin-top: 20px; font-style: italic;">
                {ats['disclaimer']}
            </p>
        """, unsafe_allow_html=True)


# PAGE 3: SKILLS GAP ANALYSIS
elif page == "📊 Skills Gap Analysis":
    st.title("In-Depth Skills Gap Analysis")
    st.caption("Deep-dive inspection into category-by-category competencies and critical TF-IDF keyword gaps.")

    if not st.session_state.match_results:
        st.info("⚠️ Please upload a resume and run an analysis on the **Analyze Resume** page to view skill gap breakdowns.")
    else:
        match = st.session_state.match_results

        # Matched vs Missing by Category Breakdown
        st.subheader("Category-Wise Skill Distribution")

        # Group matched and missing into taxonomy categories
        categories = list(skill_extractor.categories.keys())
        cat_data = []

        for cat in categories:
            cat_skills = set(skill_extractor.categories[cat])
            matched_in_cat = len([s for s in match["matched_skills"] if s in cat_skills])
            missing_in_cat = len([s for s in match["missing_skills"] if s in cat_skills])

            if matched_in_cat > 0 or missing_in_cat > 0:
                cat_data.append({
                    "Category": cat,
                    "Matched": matched_in_cat,
                    "Missing": missing_in_cat,
                    "Total": matched_in_cat + missing_in_cat
                })

        if cat_data:
            cat_df = pd.DataFrame(cat_data)
            fig_cat = go.Figure()
            fig_cat.add_trace(go.Bar(
                name="Matched Skills",
                x=cat_df["Category"],
                y=cat_df["Matched"],
                marker_color="#10B981"
            ))
            fig_cat.add_trace(go.Bar(
                name="Missing Skills",
                x=cat_df["Category"],
                y=cat_df["Missing"],
                marker_color="#EF4444"
            ))

            fig_cat.update_layout(
                barmode='group',
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(tickfont=dict(color='#E2E8F0', size=11), gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(tickfont=dict(color='#94A3B8'), gridcolor='rgba(255,255,255,0.08)'),
                legend=dict(font=dict(color='#E2E8F0')),
                margin=dict(l=10, r=10, t=20, b=30),
                height=320
            )
            st.plotly_chart(fig_cat, use_container_width=True)
        else:
            st.caption("No domain-specific taxonomy categories matched for this comparison.")

        # TF-IDF High-Impact Keyword Gaps Table
        st.subheader("TF-IDF Keyword Gap Matrix")
        st.caption("Top weighted phrases in the job description that automated keyword scanners expect to find.")

        gaps = match.get("keyword_gaps", [])
        if gaps:
            g_df = pd.DataFrame(gaps)
            # Add visual status
            g_df["Status"] = g_df["found_in_resume"].apply(lambda x: "✅ Present" if x else "❌ Missing")
            g_df = g_df[["keyword", "importance", "score", "Status"]]
            g_df.columns = ["Keyword / Phrase", "Importance", "TF-IDF Weight", "Presence"]

            st.dataframe(
                g_df,
                use_container_width=True,
                column_config={
                    "TF-IDF Weight": st.column_config.ProgressColumn(
                        "TF-IDF Weight",
                        help="Relative importance of the term in the Job Description",
                        min_value=0.0,
                        max_value=1.0,
                        format="%.3f"
                    )
                }
            )

        # Learning & Bridging Suggestions
        if match["missing_skills"]:
            st.subheader("Recommended Learning Roadmap")
            st.markdown("""
                <div class="dashboard-card">
                    <p style="font-size: 13.5px; color: #CBD5E1; margin-bottom: 8px;">
                        To increase your ATS score naturally for this role without fabricating credentials, consider building a project utilizing:
                    </p>
                    <div style="margin-bottom: 12px;">
            """, unsafe_allow_html=True)
            for sk in match["missing_skills"][:5]:
                st.markdown(f"<span class='skill-tag skill-tag-missing'>🎯 Learn {sk}</span>", unsafe_allow_html=True)
            st.markdown("""
                    </div>
                    <p style="font-size: 12.5px; color: #94A3B8; margin: 0;">
                        💡 <i>Tip: Build a self-contained portfolio demo integrating 1-2 of these tools, document it on GitHub, and add the repository link to your resume.</i>
                    </p>
                </div>
            """, unsafe_allow_html=True)


# PAGE 4: RESUME IMPROVEMENT ASSISTANT
elif page == "✍️ Resume Improvement Assistant":
    st.title("Resume Improvement Assistant")
    st.caption("Transform passive duty descriptions into high-impact, quantified accomplishments using the Google XYZ formula.")

    st.markdown("""
        <div class="dashboard-card" style="margin-bottom: 16px;">
            <b style="color: #818CF8;">The Google XYZ Principle:</b><br/>
            <span style="font-size: 13px; color: #CBD5E1;">
                <i>"Accomplished [X], as measured by [Y], by doing [Z]"</i><br/>
                Avoid vague statements like <i>"worked on microservices"</i>. Instead, state the scale, the tools used, and the measurable impact.
            </span>
        </div>
    """, unsafe_allow_html=True)

    # Preset sample bullets for quick testing
    sample_bullets = [
        "Worked on machine learning model for classifying documents.",
        "Responsible for writing backend APIs in Python and fixing bugs.",
        "Helped with frontend UI development in React and styled components.",
        "Did database optimization for slow queries.",
        "Custom (Write your own below)"
    ]
    selected_sample = st.selectbox("Select a sample weak bullet point to optimize:", sample_bullets, index=0)

    default_bullet_text = selected_sample if selected_sample != "Custom (Write your own below)" else ""

    user_bullet = st.text_area(
        "Enter Draft Bullet Point or Project Description:",
        value=default_bullet_text,
        height=100,
        placeholder="e.g. Worked on building a search pipeline using Python..."
    )

    col_role, col_btn = st.columns([2, 1])
    with col_role:
        target_spec = st.selectbox(
            "Target Engineering Domain",
            ["AI & Machine Learning", "Full Stack Software Engineering", "Data Science & Analytics", "DevOps & Cloud"]
        )
    with col_btn:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        enhance_btn = st.button("✨ Enhance Bullet Point", type="primary", use_container_width=True)

    if enhance_btn or user_bullet:
        if not user_bullet.strip():
            st.warning("Please enter a bullet point above.")
        else:
            result = bullet_assistant.enhance_bullet(user_bullet, target_role=target_spec)

            st.markdown("<br/>", unsafe_allow_html=True)
            st.subheader("Improvement Diagnostic")

            # Weaknesses detected
            if result["issues"]:
                for iss in result["issues"]:
                    st.warning(f"⚠️ {iss}")
            else:
                st.success("✅ No glaring passive phrasing detected; here are quantified STAR enhancements:")

            # Suggestions
            st.subheader("Enhanced Variations")
            for sug in result["suggestions"]:
                st.markdown(f"""
                    <div class="bullet-card">
                        <div class="bullet-title">📌 {sug['type']}</div>
                        <div class="bullet-text">{sug['text']}</div>
                        <div style="font-size: 12px; color: #94A3B8; margin-top: 6px;">
                            💡 <b>Context Guidance:</b> {sug['tip']}
                        </div>
                    </div>
                """, unsafe_allow_html=True)


# PAGE 5: ANALYSIS HISTORY
elif page == "📜 Analysis History":
    st.title("Scan History & Analytics")
    st.caption("Review previous resume scans stored locally in SQLite.")

    hist_df = db.get_history_df()

    if hist_df.empty:
        st.info("No scan history found. Run an analysis on the **Analyze Resume** page to begin logging records.")
    else:
        # High level summary
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Total Analyses", len(hist_df))
        with m2:
            st.metric("Avg ATS Score", f"{hist_df['overall_score'].mean():.1f}%")
        with m3:
            st.metric("Max ATS Score", f"{hist_df['overall_score'].max():.1f}%")
        with m4:
            st.metric("Min ATS Score", f"{hist_df['overall_score'].min():.1f}%")

        st.markdown("<br/>", unsafe_allow_html=True)

        # Plotly Score Trend
        if len(hist_df) > 1:
            trend_df = hist_df.sort_values(by="id")
            fig_trend = px.line(
                trend_df,
                x="timestamp",
                y="overall_score",
                markers=True,
                title="ATS Compatibility Score Trend",
                color_discrete_sequence=["#6366F1"]
            )
            fig_trend.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#94A3B8')),
                yaxis=dict(gridcolor='rgba(255,255,255,0.06)', tickfont=dict(color='#94A3B8'), range=[0, 105]),
                title_font=dict(color='#FFFFFF', size=14),
                margin=dict(l=10, r=10, t=40, b=20),
                height=260
            )
            st.plotly_chart(fig_trend, use_container_width=True)

        # History Table
        st.subheader("Previous Scans")
        st.dataframe(
            hist_df[["id", "timestamp", "candidate_name", "job_title", "overall_score", "rating_label", "matched_count", "missing_count"]],
            use_container_width=True,
            column_config={
                "id": "Scan ID",
                "timestamp": "Timestamp",
                "candidate_name": "Candidate",
                "job_title": "Target Role",
                "overall_score": st.column_config.NumberColumn("Score", format="%.1f%%"),
                "rating_label": "Verdict",
                "matched_count": "Matched Skills",
                "missing_count": "Missing Skills"
            }
        )

        # Actions: Delete or Clear
        del_col1, del_col2 = st.columns([1, 2])
        with del_col1:
            scan_ids = hist_df["id"].tolist()
            selected_del_id = st.selectbox("Select ID to delete:", scan_ids)
            if st.button("🗑️ Delete Selected Scan"):
                db.delete_analysis(selected_del_id)
                st.toast(f"Deleted scan #{selected_del_id}", icon="🗑️")
                st.rerun()

        with del_col2:
            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            if st.button("⚠️ Clear Entire History", type="secondary"):
                db.clear_all()
                st.toast("Scan history cleared.", icon="🧹")
                st.rerun()


# PAGE 6: ABOUT PROJECT
elif page == "ℹ️ About Project":
    st.title("About AI Resume Analyzer")
    st.caption("Intelligent ATS & Career Assistant – CSE (AI & ML) Final Year Academic & Portfolio Demonstration.")

    st.markdown("""
        <div class="dashboard-card">
            <h3 style="margin: 0 0 8px 0; color: #FFFFFF;">1. Project Objective & Vision</h3>
            <p style="font-size: 13.5px; color: #CBD5E1; line-height: 1.6;">
                The AI Resume Analyzer bridges the gap between job candidates and modern Applicant Tracking Systems (ATS).
                By employing transparent Natural Language Processing (NLP) techniques, deterministic skill taxonomy mapping,
                and explainable multi-pillar scoring, the application provides actionable career guidance without relying
                on unpredictable black-box scoring or expensive third-party APIs.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.subheader("2. System Architecture")
    st.markdown("""
```
┌─────────────────────────────────┐       ┌─────────────────────────────────┐
│     Uploaded Resume (PDF)       │       │     Target Job Description      │
└───────────────┬─────────────────┘       └────────────────┬────────────────┘
                │                                          │
                ▼                                          ▼
     [ pdfminer.six Parsing ]                    [ Keyword & Requirement ]
   • Contact channel extraction                  [ Extraction (TF-IDF)   ]
   • Section segmentation (6 areas)                        │
                │                                          │
                ▼                                          ▼
     [ Skill Taxonomy Engine ] ◄─────────────────► [ Semantic Similarity ]
   • 150+ categorized skills                       • Sublinear TF-IDF
   • Multi-alias normalization                     • Cosine Matrix Angle
   • Special symbols (C++, K8s)                            │
                │                                          │
                └───────────────────┬──────────────────────┘
                                    │
                                    ▼
                     [ Explainable ATS Scorer ]
                   • Skill Coverage (40%)
                   • Text Similarity (25%)
                   • Projects & Experience (20%)
                   • Education Alignment (15%)
                                    │
          ┌─────────────────────────┼─────────────────────────┐
          ▼                         ▼                         ▼
   [ Visual Dashboard ]    [ Report Generator ]    [ Local SQLite Log ]
   • Plotly Gauge          • ReportLab PDF         • Scan metadata
   • Breakdown Bars        • Structured CSV        • Zero PII persistence
```
    """)

    st.subheader("3. Technical Stack")
    t1, t2, t3, t4 = st.columns(4)
    with t1:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 20px;">🐍</div>
                <b style="color: #FFFFFF;">Python 3.13</b><br/>
                <span style="font-size: 12px; color: #94A3B8;">Core backend language</span>
            </div>
        """, unsafe_allow_html=True)
    with t2:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 20px;">⚡</div>
                <b style="color: #FFFFFF;">Streamlit</b><br/>
                <span style="font-size: 12px; color: #94A3B8;">Reactive web interface</span>
            </div>
        """, unsafe_allow_html=True)
    with t3:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 20px;">🔬</div>
                <b style="color: #FFFFFF;">Scikit-learn</b><br/>
                <span style="font-size: 12px; color: #94A3B8;">TF-IDF & Cosine Similarity</span>
            </div>
        """, unsafe_allow_html=True)
    with t4:
        st.markdown("""
            <div class="metric-card">
                <div style="font-size: 20px;">📄</div>
                <b style="color: #FFFFFF;">ReportLab</b><br/>
                <span style="font-size: 12px; color: #94A3B8;">PDF Report Generation</span>
            </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.subheader("4. Ethical AI & Disclaimers")
    st.markdown("""
        <div class="dashboard-card" style="border-left: 4px solid #6366F1;">
            <ul style="margin: 0; padding-left: 18px; color: #CBD5E1; font-size: 13px; line-height: 1.6;">
                <li><b>No Automated Hiring or Rejection:</b> This tool provides educational guidance to help candidates present their genuine skills effectively. It does not make employment decisions.</li>
                <li><b>No Demographic Profiling:</b> Candidate evaluation relies strictly on technical skills, education, and experience keywords. Age, gender, race, or nationality are never analyzed or extracted.</li>
                <li><b>Privacy Safeguards:</b> All processing occurs locally on your machine. Resumes are not transmitted to external servers or commercial AI data harvesters.</li>
            </ul>
        </div>
    """, unsafe_allow_html=True)
