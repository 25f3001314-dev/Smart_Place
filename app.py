"""
SmartPlace - AI-Powered Campus Placement Portal
TECHNOVUS Hackathon MVP | Run: streamlit run app.py
"""
import streamlit as st
import time

from ml_model import ml_fit_score, SmartMatchEngine
from resume_generator import generate_resume

# Gemini AI Setup
try:
    from google import genai as _genai
    GEMINI_API_KEY = "AIzaSyAF8__endrkuZVDpmW7wkbPsTjhO3w6JnI"
    _genai_client = _genai.Client(api_key=GEMINI_API_KEY)
    GEMINI_AVAILABLE = True
except Exception:
    GEMINI_AVAILABLE = False
    _genai_client = None

_engine = SmartMatchEngine()

def gemini_generate(prompt: str, fallback: str = "") -> str:
    if not GEMINI_AVAILABLE or _genai_client is None:
        return fallback
    try:
        response = _genai_client.models.generate_content(
            model="models/gemini-2.5-flash-lite",
            contents=prompt,
        )
        return response.text.strip()
    except Exception as e:
        return fallback or f"Gemini unavailable: {e}"

st.set_page_config(
    page_title="SmartPlace | AI Placement Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #F0F2F8 !important;
    font-family: 'Segoe UI', Roboto, sans-serif;
}
[data-testid="block-container"] { background: transparent !important; padding-top: 1.5rem !important; }
[data-testid="stMainBlockContainer"] { background: transparent !important; }
h1, h2, h3 { color: #1A237E !important; font-weight: 700; }
p, li { color: #263238; }

section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1A237E 0%, #283593 60%, #1565C0 100%) !important;
    border-right: 1px solid #3949AB;
}
section[data-testid="stSidebar"] *:not(input):not(select):not(option) { color: #FFFFFF !important; }
section[data-testid="stSidebar"] input {
    background: rgba(255,255,255,0.15) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
    caret-color: #FFFFFF;
}
section[data-testid="stSidebar"] input::placeholder { color: rgba(255,255,255,0.55) !important; }
section[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div {
    background: rgba(255,255,255,0.15) !important;
    color: #FFFFFF !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    border-radius: 8px !important;
}
section[data-testid="stSidebar"] [data-testid="stSelectbox"] svg { fill: #FFFFFF !important; }
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stTextInput label,
section[data-testid="stSidebar"] .stSelectbox label {
    color: #B0BEC5 !important; font-size: 12px !important;
    font-weight: 600 !important; letter-spacing: 0.5px;
}
section[data-testid="stSidebar"] .stButton > button {
    background: linear-gradient(135deg, #00BCD4, #0097A7) !important;
    color: #FFFFFF !important; border: none !important;
    border-radius: 10px !important; font-weight: 700 !important;
    font-size: 15px !important; padding: 10px !important; width: 100%;
    box-shadow: 0 4px 12px rgba(0,188,212,0.4);
}
section[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.2) !important; }

.hero-section {
    background: linear-gradient(135deg, #1A237E 0%, #283593 40%, #1565C0 100%);
    border-radius: 20px; padding: 60px 40px; text-align: center;
    margin-bottom: 30px; box-shadow: 0 8px 32px rgba(26,35,126,0.3);
}
.hero-section h1 { color: #FFFFFF !important; font-size: 52px; margin-bottom: 8px; }
.hero-section h3 { color: #B2EBF2 !important; font-weight: 400; margin-bottom: 16px; }
.hero-section p  { color: #E3F2FD !important; font-size: 16px; max-width: 600px; margin: 0 auto 12px; }
.hero-hint       { color: #80DEEA !important; font-size: 13px; }

div[data-testid="metric-container"] {
    background: #FFFFFF !important; border: 1px solid #C5CAE9;
    border-top: 4px solid #3949AB; border-radius: 14px;
    padding: 18px; box-shadow: 0 4px 14px rgba(0,0,0,0.07);
}
div[data-testid="metric-container"] label { color: #546E7A !important; font-size: 13px !important; font-weight: 600 !important; }
div[data-testid="metric-container"] [data-testid="stMetricValue"] { color: #1A237E !important; font-size: 28px !important; font-weight: 800 !important; }

.job-card {
    background: #FFFFFF; border: 1px solid #E8EAF6;
    border-left: 5px solid #3949AB; border-radius: 14px;
    padding: 20px 24px; margin-bottom: 18px;
    box-shadow: 0 3px 12px rgba(0,0,0,0.06);
    transition: transform 0.2s, box-shadow 0.2s;
}
.job-card:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(57,73,171,0.15); border-left-color: #00ACC1; }
.job-title { font-size: 17px; font-weight: 700; color: #1A237E; margin-bottom: 2px; }
.company   { font-size: 13px; color: #546E7A; margin-bottom: 8px; }
.tag { display: inline-block; background: #E8EAF6; color: #3949AB; border-radius: 20px; padding: 3px 11px; font-size: 11px; margin: 2px 3px 2px 0; font-weight: 600; }
.score-badge { float: right; background: linear-gradient(135deg,#00897B,#26A69A); color: #fff; border-radius: 20px; padding: 5px 16px; font-weight: 800; font-size: 14px; }
.notif { background: #FFFDE7; border-left: 4px solid #F9A825; border-radius: 10px; padding: 12px 18px; margin-bottom: 10px; font-size: 13px; color: #37474F; }
button[data-baseweb="tab"] { font-weight: 600 !important; font-size: 14px !important; color: #546E7A !important; }
button[data-baseweb="tab"][aria-selected="true"] { color: #1A237E !important; border-bottom: 3px solid #3949AB !important; }
::-webkit-scrollbar { width: 6px; } ::-webkit-scrollbar-track { background: #F0F2F8; }
::-webkit-scrollbar-thumb { background: #9FA8DA; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

USERS = {
    "ashutosh":  ("pass123",   "student", "Ashutosh Shri Mishra"),
    "priya":     ("priya@456", "student", "Priya Sharma"),
    "rahul":     ("rahul@789", "student", "Rahul Verma"),
    "deepak":    ("deep@321",  "student", "Deepak Pal"),
    "placement": ("admin@NIT", "cell",    "Placement Cell - NIT Agartala"),
}

JOBS = [
    {"id":1,  "title":"Data Scientist",           "company":"Google India",   "location":"Bengaluru", "ctc":"28 LPA",    "skills":["python","machine learning","statistics","sql","tensorflow"],          "desc":"Work on large-scale ML pipelines and recommendation systems."},
    {"id":2,  "title":"ML Engineer",              "company":"Flipkart",       "location":"Bengaluru", "ctc":"22 LPA",    "skills":["python","xgboost","mlflow","docker","scikit-learn"],                  "desc":"Build and deploy production ML models for e-commerce use-cases."},
    {"id":3,  "title":"NLP Research Engineer",    "company":"Microsoft",      "location":"Hyderabad", "ctc":"30 LPA",    "skills":["python","nlp","transformers","pytorch","bert"],                        "desc":"Advance conversational AI and language understanding research."},
    {"id":4,  "title":"AI/ML Intern",             "company":"NVIDIA",         "location":"Pune",      "ctc":"80K/month", "skills":["python","deep learning","cuda","pytorch","computer vision"],           "desc":"6-month internship on GPU-accelerated AI training pipelines."},
    {"id":5,  "title":"Data Analyst",             "company":"Razorpay",       "location":"Remote",    "ctc":"12 LPA",    "skills":["sql","python","power bi","excel","statistics"],                        "desc":"Drive business decisions through data-driven insights."},
    {"id":6,  "title":"Software Engineer",        "company":"Zepto",          "location":"Mumbai",    "ctc":"18 LPA",    "skills":["java","spring boot","microservices","kafka","postgresql"],             "desc":"Build scalable backend services for quick-commerce platform."},
    {"id":7,  "title":"Frontend Developer",       "company":"Swiggy",         "location":"Bengaluru", "ctc":"16 LPA",    "skills":["react","javascript","typescript","css","redux"],                       "desc":"Create pixel-perfect UIs for millions of daily active users."},
    {"id":8,  "title":"Blockchain Developer",     "company":"Polygon",        "location":"Remote",    "ctc":"20 LPA",    "skills":["solidity","ethereum","web3.js","smart contracts","python"],           "desc":"Develop DeFi protocols and NFT infrastructure on Polygon chain."},
    {"id":9,  "title":"MLOps Engineer",           "company":"Infosys",        "location":"Hyderabad", "ctc":"14 LPA",    "skills":["mlflow","docker","kubernetes","python","ci/cd"],                      "desc":"Automate ML lifecycle: training, monitoring and deployment."},
    {"id":10, "title":"Quantitative Analyst",     "company":"Goldman Sachs",  "location":"Bengaluru", "ctc":"35 LPA",    "skills":["python","statistics","linear algebra","r","machine learning"],        "desc":"Build quant models for risk management and algorithmic trading."},
]

SAMPLE_STUDENTS = [
    {"Name":"Ashutosh Shri Mishra","Branch":"CSE","CGPA":8.5,"Skills":"Python, ML, XGBoost, NLP, Scikit-learn, Pandas",          "Status":"Shortlisted",          "Company":"Flipkart"},
    {"Name":"Priya Sharma",        "Branch":"ECE","CGPA":8.9,"Skills":"Python, Deep Learning, Computer Vision, PyTorch",          "Status":"Offer Received",       "Company":"NVIDIA"},
    {"Name":"Rahul Verma",         "Branch":"IT", "CGPA":7.8,"Skills":"Java, Spring Boot, Microservices, Kafka, PostgreSQL",      "Status":"Applied",              "Company":"Zepto"},
    {"Name":"Deepak Pal",          "Branch":"CSE","CGPA":8.1,"Skills":"React, JavaScript, TypeScript, CSS, Redux",                "Status":"Interview Scheduled",  "Company":"Swiggy"},
    {"Name":"Sneha Gupta",         "Branch":"CSE","CGPA":9.1,"Skills":"Python, Statistics, SQL, Power BI, R",                     "Status":"Offer Received",       "Company":"Goldman Sachs"},
    {"Name":"Arjun Singh",         "Branch":"CSE","CGPA":8.3,"Skills":"Python, NLP, Transformers, BERT, PyTorch",                 "Status":"Shortlisted",          "Company":"Microsoft"},
    {"Name":"Ritika Das",          "Branch":"ECE","CGPA":7.5,"Skills":"Solidity, Ethereum, Web3.js, Smart Contracts, Python",     "Status":"Applied",              "Company":"Polygon"},
    {"Name":"Saurav Kumar",        "Branch":"ME", "CGPA":7.2,"Skills":"Python, SQL, Excel, Power BI, Statistics",                 "Status":"Applied",              "Company":"Razorpay"},
    {"Name":"Anjali Roy",          "Branch":"IT", "CGPA":8.7,"Skills":"Python, MLflow, Docker, Kubernetes, CI/CD",                "Status":"Interview Scheduled",  "Company":"Infosys"},
    {"Name":"Vikram Nair",         "Branch":"CSE","CGPA":9.3,"Skills":"Python, Statistics, Linear Algebra, R, Machine Learning",  "Status":"Offer Received",       "Company":"Goldman Sachs"},
]

if "logged_in" not in st.session_state:
    st.session_state.logged_in    = False
    st.session_state.role         = None
    st.session_state.username     = None
    st.session_state.display      = None
    st.session_state.notifs       = []
    st.session_state.applications = {}

def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

def score_color(score: int) -> str:
    if score >= 80: return "#00897B"
    elif score >= 60: return "#FB8C00"
    return "#E53935"

def render_job_card(job: dict, score: int, applied: bool):
    tags_html = "".join(f'<span class="tag">{s}</span>' for s in job["skills"])
    st.markdown(f"""
    <div class="job-card">
        <span class="score-badge" style="background:linear-gradient(135deg,{score_color(score)},{score_color(score)}CC)">
            {score}% Match
        </span>
        <div class="job-title">{job["title"]}</div>
        <div class="company">🏢 {job["company"]} &nbsp;|&nbsp; 📍 {job["location"]} &nbsp;|&nbsp; 💰 {job["ctc"]}</div>
        <p style="font-size:13px;color:#546E7A;margin:6px 0 8px">{job["desc"]}</p>
        {tags_html}
    </div>
    """, unsafe_allow_html=True)
    label = "✅ Applied" if applied else "🚀 Apply Now"
    return st.button(label, key=f"apply_{job['id']}", disabled=applied, use_container_width=False)

# SIDEBAR
with st.sidebar:
    st.markdown("## 🎓 SmartPlace")
    st.markdown("*AI-Powered Campus Portal*")
    st.divider()

    if not st.session_state.logged_in:
        st.markdown("### 🔐 Login")
        username  = st.text_input("Username", placeholder="e.g. ashutosh")
        password  = st.text_input("Password", type="password")
        role_hint = st.selectbox("Login as", ["Student", "Placement Cell"])

        if st.button("🚀 Login", use_container_width=True):
            if username in USERS:
                pwd, role, display = USERS[username]
                expected = "cell" if role_hint == "Placement Cell" else "student"
                if pwd == password and role == expected:
                    st.session_state.logged_in    = True
                    st.session_state.role         = role
                    st.session_state.username     = username
                    st.session_state.display      = display
                    st.session_state.notifs       = [
                        "📢 Campus Drive: Google India - Sept 5, 2026",
                        "📢 Off-Campus: Flipkart ML Engineer - Apply by Aug 30",
                        "🔔 Your profile was viewed by 3 recruiters this week!",
                    ]
                    st.rerun()
                else:
                    st.error("Invalid credentials or role mismatch.")
            else:
                st.error("User not found.")

        st.divider()
        st.markdown("""
        <div style="background:rgba(255,255,255,0.18);border-radius:10px;padding:12px 14px;
                    margin-top:4px;border:1px solid rgba(255,255,255,0.35)">
            <div style="color:#FFD700;font-size:11px;font-weight:700;letter-spacing:1px;
                        margin-bottom:8px">DEMO ACCOUNTS</div>
            <div style="color:#fff;font-size:13px;margin-bottom:2px"><b>🎓 Student</b></div>
            <div style="color:#E0E7FF;font-size:12px;font-family:monospace;margin-bottom:8px">
                ashutosh &nbsp;/&nbsp; pass123</div>
            <div style="color:#fff;font-size:13px;margin-bottom:2px"><b>🏢 Placement Cell</b></div>
            <div style="color:#E0E7FF;font-size:12px;font-family:monospace">
                placement &nbsp;/&nbsp; admin@NIT</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        st.markdown(f"### 👋 {st.session_state.display}")
        st.markdown(f"`{st.session_state.role.upper()}`")
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            logout()

# LANDING PAGE
if not st.session_state.logged_in:
    st.markdown("""
    <div class="hero-section">
        <h1>🎓 SmartPlace</h1>
        <h3>AI-Powered Campus Placement Portal</h3>
        <p>Match your skills to dream jobs with TF-IDF ML scoring, generate
        ATS-ready resumes in one click, and track your placement journey -
        built for Indian engineering colleges like NIT Agartala.</p>
        <p class="hero-hint">← Login from the sidebar to get started</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    for col, icon, title, body in [
        (col1, "🤖", "AI Job Matching",  "TF-IDF cosine similarity scores every job against your exact skillset in real-time."),
        (col2, "📄", "Resume Builder",   "Generate ATS-optimised PDF resume from your profile in one click via reportlab."),
        (col3, "📊", "Live Dashboard",   "Placement Cell tracks all students, ML fit scores, and hiring statuses live."),
    ]:
        with col:
            st.markdown(f"""
            <div class="job-card" style="text-align:center;border-left:5px solid #00897B">
                <div style="font-size:36px">{icon}</div>
                <div class="job-title" style="margin:8px 0 6px">{title}</div>
                <div style="font-size:13px;color:#546E7A">{body}</div>
            </div>""", unsafe_allow_html=True)
    st.stop()

# STUDENT VIEW
if st.session_state.role == "student":
    tab_jobs, tab_profile, tab_resume, tab_notifs = st.tabs([
        "🔍 Job Board", "👤 My Profile", "📄 Resume Builder", "🔔 Notifications"
    ])

    # TAB 1: JOB BOARD
    with tab_jobs:
        st.markdown("## 🔍 AI Job Board")
        st.markdown("*Scores computed live using TF-IDF cosine similarity*")
        quick_skills = st.text_input(
            "⚡ Your Skills (comma-separated) - updates scores instantly",
            value="Python, Machine Learning, XGBoost, Scikit-learn, SQL, Pandas, NLP",
            help="Type your actual skills for accurate matching"
        )
        min_score = st.slider("Show jobs with match >=", 0, 90, 40, 5)
        student_text = quick_skills.replace(",", " ").lower()
        job_texts    = [" ".join(j["skills"]) for j in JOBS]
        scores       = ml_fit_score(student_text, job_texts)
        job_score_pairs = sorted(zip(JOBS, scores), key=lambda x: x[1], reverse=True)
        filtered = [(j, s) for j, s in job_score_pairs if s >= min_score]
        st.markdown(f"**{len(filtered)} jobs** match your filter (out of {len(JOBS)} total)")
        st.divider()

        if not filtered:
            st.info("No jobs meet your filter. Lower the minimum score or add more skills.")
        else:
            cols = st.columns(2)
            for idx, (job, score) in enumerate(filtered):
                with cols[idx % 2]:
                    applied = st.session_state.applications.get(job["id"], False)
                    clicked = render_job_card(job, score, applied)
                    if clicked and not applied:
                        st.session_state.applications[job["id"]] = True
                        st.session_state.notifs.insert(0, f"✅ Applied to {job['title']} at {job['company']}!")
                        st.rerun()
                    # Feature B: Why I Match
                    why_key = f"why_{job['id']}"
                    if st.button("💡 Why I Match?", key=f"why_btn_{job['id']}", use_container_width=True):
                        with st.spinner("Gemini is analysing your fit..."):
                            prompt = (
                                f"Compare student profile ({quick_skills}) with "
                                f"Job: {job['title']} at {job['company']} requiring {', '.join(job['skills'])}. "
                                f"Give exactly 1 persuasive sentence (max 30 words) why this student is a strong fit. "
                                f"Be specific. No preamble."
                            )
                            fallback = (
                                f"Your expertise in {', '.join(job['skills'][:2])} directly aligns with "
                                f"{job['company']}'s core requirements, making you a {score}% skill match."
                            )
                            st.session_state[why_key] = gemini_generate(prompt, fallback)
                    if why_key in st.session_state:
                        st.markdown(
                            f"<div style='background:#E3F2FD;border-left:3px solid #1565C0;"
                            f"border-radius:6px;padding:10px 14px;font-size:13px;color:#0D47A1;margin-bottom:8px'>"
                            f"💬 <b>Why you match:</b> {st.session_state[why_key]}</div>",
                            unsafe_allow_html=True
                        )

    # TAB 2: PROFILE
    with tab_profile:
        st.markdown("## 👤 Student Profile")
        c1, c2 = st.columns(2)
        with c1:
            p_name    = st.text_input("Full Name",      value=st.session_state.display)
            p_email   = st.text_input("Email",          value=f"{st.session_state.username}@nitagt.ac.in")
            p_phone   = st.text_input("Phone",          value="+91-9876543210")
            p_college = st.text_input("College",        value="NIT Agartala")
        with c2:
            p_branch  = st.text_input("Branch & Year",  value="B.Tech CSE | 2022-2026")
            p_cgpa    = st.number_input("CGPA (out of 10)", 0.0, 10.0, 8.5, 0.1)
            p_linkedin= st.text_input("LinkedIn URL",   value="linkedin.com/in/yourprofile")
            p_github  = st.text_input("GitHub URL",     value="github.com/yourusername")

        st.markdown("#### 🛠 Skills")
        p_skills = st.text_area("Skills (comma-separated)",
            value="Python, Machine Learning, XGBoost, Scikit-learn, Pandas, NumPy, SQL, Power BI, Streamlit, Git, NLP",
            height=80)

        st.markdown("#### 📝 Projects")
        p_proj1_title = st.text_input("Project 1 Title", value="SmartPlace - AI Placement Portal")
        p_proj1_desc  = st.text_area("Project 1 Description",
            value="Built Streamlit MVP with TF-IDF job matching engine\nIntegrated reportlab PDF resume generator\nAchieved 95% skill-match accuracy on test dataset",
            height=90, key="pd1")
        p_proj2_title = st.text_input("Project 2 Title", value="Jal-Drishti - Water Intelligence Dashboard")
        p_proj2_desc  = st.text_area("Project 2 Description",
            value="Predicted AI data-centre water usage with LSTM\nVisualised India sector-wise water data via Power BI",
            height=90, key="pd2")

        st.markdown("#### 💼 Internship / Experience")
        i_role     = st.text_input("Role",     value="Data Science Intern")
        i_company  = st.text_input("Company",  value="Statistella")
        i_duration = st.text_input("Duration", value="Jan 2025 - Mar 2025")
        i_desc     = st.text_area("Description",
            value="Ranked Top-5 in BASH 8.0 Round-2 ML competition\nBuilt ensemble XGBoost + LightGBM pipeline",
            height=80, key="id1")

        st.markdown("#### 🏆 Achievements")
        p_ach = st.text_area("One achievement per line",
            value="TECHNOVUS Hackathon - SmartPlace Finalist\nBASH 8.0 by Statistella - Top 5 Nationally\nEast India Blockchain Summit 2025 - Speaker",
            height=90)

        st.session_state["profile"] = dict(
            name=p_name, email=p_email, phone=p_phone, college=p_college,
            branch=p_branch, cgpa=p_cgpa, linkedin=p_linkedin, github=p_github,
            skills=[s.strip() for s in p_skills.split(",") if s.strip()],
            projects=[
                {"title": p_proj1_title, "desc": p_proj1_desc},
                {"title": p_proj2_title, "desc": p_proj2_desc},
            ],
            internships=[{"role": i_role, "company": i_company, "duration": i_duration, "desc": i_desc}],
            achievements=[a for a in p_ach.split("\n") if a.strip()],
        )
        st.success("✅ Profile auto-saved - go to Resume Builder to download PDF.")

    # TAB 3: RESUME BUILDER
    with tab_resume:
        st.markdown("## 📄 ATS-Optimised Resume Builder")
        st.markdown("Your profile data is pulled automatically. Click **Generate Resume** to create a professional PDF.")

        st.markdown("### 🤖 AI Resume Bullet Generator")
        st.markdown("*Powered by Gemini 2.5 Flash Lite - generates ATS-optimised bullet points.*")

        ai_skills = st.text_input("Your Skills (for AI bullets)",
            value=", ".join(st.session_state.get("profile", {}).get("skills", ["Python","ML","XGBoost","NLP","Streamlit"])),
            key="ai_skills_input")
        ai_projects = st.text_area("Your Projects (brief description)",
            value="\n".join([p["title"] + ": " + p["desc"].split("\n")[0]
                for p in st.session_state.get("profile", {}).get("projects",
                    [{"title":"SmartPlace","desc":"AI placement portal with TF-IDF matching"}])]),
            height=80, key="ai_projects_input")

        if st.button("✨ Generate AI Resume Bullets", type="primary", key="gen_bullets"):
            with st.spinner("Gemini is crafting your ATS bullets..."):
                prompt = (
                    f"You are a professional resume writer for Indian engineering students. "
                    f"Based on skills: {ai_skills} and projects: {ai_projects}, "
                    f"generate exactly 5 high-impact ATS-optimized resume bullet points. "
                    f"Each bullet must: start with a strong action verb (Built, Developed, Engineered, Designed, Achieved), "
                    f"include quantifiable metrics, be under 20 words, relevant to data science or ML roles. "
                    f"Output as a numbered list only. No extra commentary."
                )
                fallback = (
                    "1. Engineered TF-IDF cosine similarity engine achieving 95% job-match precision\n"
                    "2. Developed XGBoost ensemble model ranked Top-5 in BASH 8.0 ML competition\n"
                    "3. Built Streamlit MVP with PDF resume generator serving 50+ student profiles\n"
                    "4. Designed NLP pipeline processing 10K+ job descriptions with <300ms latency\n"
                    "5. Achieved CGPA 8.5/10 while delivering 3 production-grade ML projects"
                )
                st.session_state["ai_bullets"] = gemini_generate(prompt, fallback)

        if "ai_bullets" in st.session_state:
            st.markdown("""
            <div style='background:#E8F5E9;border-left:4px solid #00897B;border-radius:8px;padding:16px;margin:12px 0'>
                <div style='font-weight:700;color:#1B5E20;margin-bottom:8px'>✅ AI-Generated Resume Bullets</div>
            </div>""", unsafe_allow_html=True)
            st.code(st.session_state["ai_bullets"], language=None)

        st.divider()
        st.markdown("### 🖨️ Download PDF Resume")
        if st.button("🖨️ Generate Resume PDF", use_container_width=True, type="primary", key="gen_pdf"):
            prof = st.session_state.get("profile", {})
            if not prof:
                st.warning("Please fill in your profile first (Profile tab).")
            else:
                with st.spinner("Generating your ATS-optimised resume..."):
                    try:
                        pdf_bytes = generate_resume(**prof)
                        st.success("✅ Resume generated! Click below to download.")
                        st.download_button(
                            label="⬇️ Download Resume (PDF)",
                            data=pdf_bytes,
                            file_name=f"{prof['name'].replace(' ','_')}_Resume.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    except Exception as e:
                        st.error(f"Error generating PDF: {e}")

        st.divider()
        st.markdown("#### 💡 ATS Tips")
        for tip in [
            "Use keywords directly from job descriptions in your skills section.",
            "Quantify achievements: 'Improved model accuracy by 12%' beats 'Improved accuracy'.",
            "Keep to 1 page for freshers, 2 pages for experienced candidates.",
            "Avoid tables, images, or fancy fonts - ATS parsers prefer plain text layout.",
            "Use standard section headings: Education, Skills, Projects, Experience.",
        ]:
            st.markdown(f"- {tip}")

    # TAB 4: NOTIFICATIONS
    with tab_notifs:
        st.markdown("## 🔔 Notifications")
        if not st.session_state.notifs:
            st.info("No notifications yet.")
        for n in st.session_state.notifs:
            st.markdown(f'<div class="notif">{n}</div>', unsafe_allow_html=True)

# PLACEMENT CELL VIEW
elif st.session_state.role == "cell":
    st.markdown("## 🏛️ Placement Cell Dashboard - NIT Agartala")
    st.markdown("*Real-time overview of all students, ML fit scores, and placement status*")

    # CSV Upload
    with st.expander("📂 Upload Student Data (CSV)", expanded=False):
        st.markdown("Upload a CSV with columns: `Name, Branch, CGPA, Skills, Status, Company`")
        st.download_button(
            label="⬇️ Download Sample CSV Template",
            data=open("students.csv", "rb").read(),
            file_name="students_template.csv",
            mime="text/csv",
        )
        uploaded = st.file_uploader("Upload students.csv", type=["csv"], key="csv_upload")
        if uploaded:
            try:
                import io, csv
                content = uploaded.read().decode("utf-8")
                reader  = csv.DictReader(io.StringIO(content))
                loaded  = []
                for row in reader:
                    loaded.append({
                        "Name":    row.get("Name","").strip(),
                        "Branch":  row.get("Branch","").strip(),
                        "CGPA":    float(row.get("CGPA", 0)),
                        "Skills":  row.get("Skills","").strip(),
                        "Status":  row.get("Status","Applied").strip(),
                        "Company": row.get("Company","-").strip(),
                    })
                if loaded:
                    st.session_state["uploaded_students"] = loaded
                    st.success(f"✅ Loaded {len(loaded)} students from CSV!")
            except Exception as e:
                st.error(f"CSV parse error: {e}")

    students    = st.session_state.get("uploaded_students", SAMPLE_STUDENTS)
    total       = len(students)
    placed      = sum(1 for s in students if s["Status"] == "Offer Received")
    shortlisted = sum(1 for s in students if s["Status"] in ("Shortlisted","Interview Scheduled"))
    avg_cgpa    = sum(s["CGPA"] for s in students) / total

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("👥 Total Students",          total)
    m2.metric("🏆 Offers Received",         placed,      delta=f"{placed/total*100:.0f}%")
    m3.metric("📋 Shortlisted/Interview",   shortlisted)
    m4.metric("📈 Avg CGPA",                f"{avg_cgpa:.2f}")
    st.divider()

    # ML Fit Score Engine
    st.markdown("#### 🤖 ML Fit Score Engine")
    target_job   = st.selectbox("Select a job to score all students against:",
                                [f"{j['title']} @ {j['company']}" for j in JOBS])
    job_idx      = [f"{j['title']} @ {j['company']}" for j in JOBS].index(target_job)
    selected_job = JOBS[job_idx]
    job_text     = " ".join(selected_job["skills"])
    st.markdown(f"**Job:** `{selected_job['title']}` @ **{selected_job['company']}** | "
                f"Required: `{', '.join(selected_job['skills'])}`")

    scored = []
    for s in students:
        sc = ml_fit_score(s["Skills"].replace(","," ").lower(), [job_text])
        scored.append({**s, "ML Fit Score (%)": sc[0] if sc else 0})
    scored.sort(key=lambda x: x["ML Fit Score (%)"], reverse=True)

    STATUS_COLORS = {
        "Offer Received":       ("#1B5E20","#E8F5E9"),
        "Shortlisted":          ("#0D47A1","#E3F2FD"),
        "Interview Scheduled":  ("#E65100","#FFF3E0"),
        "Applied":              ("#546E7A","#ECEFF1"),
    }

    rows_html = ""
    for i, s in enumerate(scored):
        bg_s, fg_s = STATUS_COLORS.get(s["Status"], ("#546E7A","#ECEFF1"))
        sc_val = s["ML Fit Score (%)"]
        bg_m   = "#00897B" if sc_val >= 70 else "#FB8C00" if sc_val >= 50 else "#E53935"
        fg_m   = "white"
        rows_html += f"""
        <tr style="background:{'#F8F9FA' if i%2==0 else '#FFFFFF'}">
            <td style='padding:10px;font-weight:600'>{s['Name']}</td>
            <td style='padding:10px'>{s['Branch']}</td>
            <td style='padding:10px'>{s['CGPA']}</td>
            <td style='padding:10px;font-size:12px;max-width:200px'>{s['Skills'][:60]}...</td>
            <td style='padding:10px'>
                <span style='background:{bg_s};color:{fg_s};border-radius:6px;padding:3px 9px;font-size:12px;font-weight:600'>
                    {s['Status']}
                </span>
            </td>
            <td style='padding:10px'>
                <span style='background:{bg_m};color:{fg_m};border-radius:6px;padding:3px 9px;font-weight:700'>
                    {sc_val}%
                </span>
            </td>
        </tr>"""

    st.markdown(f"""
    <div style='overflow-x:auto'>
    <table style='width:100%;border-collapse:collapse;font-size:13px'>
        <thead>
            <tr style='background:#1A237E;color:white'>
                <th style='padding:10px;text-align:left'>Name</th>
                <th style='padding:10px;text-align:left'>Branch</th>
                <th style='padding:10px;text-align:left'>CGPA</th>
                <th style='padding:10px;text-align:left'>Skills</th>
                <th style='padding:10px;text-align:left'>Status</th>
                <th style='padding:10px;text-align:left'>ML Fit Score</th>
            </tr>
        </thead>
        <tbody>{rows_html}</tbody>
    </table></div>
    """, unsafe_allow_html=True)

    st.divider()

    # Feature C: Interview Prep
    st.markdown("#### 🎯 AI Interview Prep Generator")
    st.markdown("*Select a student and generate technical interview questions powered by Gemini.*")
    sel_name    = st.selectbox("Select Student", [s["Name"] for s in students], key="interview_student")
    sel_student = next(s for s in students if s["Name"] == sel_name)

    if st.button("🧠 Generate Interview Questions", type="primary", key="gen_interview"):
        with st.spinner(f"Gemini is preparing questions for {sel_name}..."):
            prompt = (
                f"Act as a senior technical interviewer at {selected_job['company']}. "
                f"Student profile: Skills: {sel_student['Skills']}, CGPA: {sel_student['CGPA']}, "
                f"Branch: {sel_student['Branch']}. "
                f"Generate exactly 3 tough, specific technical interview questions for the role of "
                f"{selected_job['title']}. Focus on their listed skills and projects. "
                f"Number them 1-3. No preamble or extra commentary."
            )
            fallback = (
                f"1. Explain the difference between XGBoost and LightGBM gradient boosting - "
                f"when would you choose one over the other?\n"
                f"2. How would you handle class imbalance in a production ML model for {selected_job['company']}?\n"
                f"3. Walk me through how you would design an end-to-end ML pipeline from data ingestion to deployment."
            )
            st.session_state["interview_qs"] = gemini_generate(prompt, fallback)

    if "interview_qs" in st.session_state:
        st.markdown(f"""
        <div style='background:#FFF3E0;border-left:4px solid #E65100;border-radius:8px;padding:16px;margin:12px 0'>
            <div style='font-weight:700;color:#BF360C;margin-bottom:8px'>
                🎯 Interview Questions for {sel_name} - {selected_job['title']} @ {selected_job['company']}
            </div>
        </div>""", unsafe_allow_html=True)
        st.code(st.session_state["interview_qs"], language=None)

    st.divider()

    # Status Distribution
    st.markdown("#### 📊 Placement Status Distribution")
    status_counts = {}
    for s in students:
        status_counts[s["Status"]] = status_counts.get(s["Status"], 0) + 1
    cols = st.columns(len(status_counts))
    for i, (status, count) in enumerate(status_counts.items()):
        with cols[i]:
            st.metric(status, count)
