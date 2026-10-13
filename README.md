# 🎯 AI Resume Analyzer – Intelligent ATS & Career Assistant

[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30+-FF4B4B.svg)](https://streamlit.io/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-1.3+-F7931E.svg)](https://scikit-learn.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-brightgreen.svg)]()

> An end-to-end, privacy-preserving AI web application that parses PDF resumes, benchmarks them against job descriptions via TF-IDF cosine similarity, calculates a 0–100 transparent ATS compatibility score, uncovers keyword gaps, and generates actionable resume improvements.

---

## 📌 Table of Contents
1. [Project Overview](#1-project-overview)
2. [Key Features](#2-key-features)
3. [System Architecture](#3-system-architecture)
4. [Explainable ATS Scoring Model](#4-explainable-ats-scoring-model)
5. [Technology Stack](#5-technology-stack)
6. [Project Structure](#6-project-structure)
7. [Getting Started (Windows & VS Code)](#7-getting-started-windows--vs-code)
8. [Usage Guide](#8-usage-guide)
9. [Running Tests](#9-running-tests)
10. [Troubleshooting](#10-troubleshooting)
11. [Deployment Guide](#11-deployment-guide)
12. [Ethical AI & Compliance](#12-ethical-ai--compliance)

---

## 1. Project Overview
Modern Applicant Tracking Systems (ATS) automatically filter through thousands of candidate resumes before human recruiters ever inspect them. Candidates often fail automated screens due to mismatched keywords, unstructured styling, missing technical competencies, or passive phraseology.

**AI Resume Analyzer** empowers job seekers and academic evaluators with:
- **Zero API Dependency:** Fully operational locally without expensive OpenAI/Gemini subscriptions or third-party cloud data harvesting.
- **Explainable Metrics:** Does not rely on a black-box model; every point in the 0–100 compatibility score is accounted for via transparent NLP mathematics.
- **Privacy First:** Raw resumes and private personal information are processed in memory and never sent to external servers or logged in plain text.
- **Ready for Academic Review:** Complete CSE (AI & ML) final-year capstone project with modular architecture, unit tests, and pre-built synthetic test samples.

---

## 2. Key Features

### 📄 Accurate PDF Parsing & Information Extraction
- Secure PDF extraction using `pdfminer.six`.
- Validates file extensions, size limits (up to 10MB), and corrupt/unreadable files.
- Extracts candidate name, email, phone number, LinkedIn, GitHub, and portfolio URLs.
- Segments resumes into standard sections: *Professional Summary, Skills, Work Experience, Technical Projects, Education, and Certifications*.
- Calculates reading metrics: page count, word count, estimated reading time.

### 🧠 Intelligent Skill Taxonomy & Normalization
- Pre-configured dataset (`data/skills.json`) classifying 150+ skills across 7 domains:
  - *Programming Languages, Web & Frameworks, AI & Machine Learning, Cloud & DevOps, Databases & Big Data, Developer Tools, and Core Soft Skills*.
- Robust alias mapping (e.g., `React.js` → `React`, `K8s` → `Kubernetes`, `AWS` → `Amazon Web Services`).
- Boundary-safe regular expressions supporting special characters like `C++`, `C#`, `.NET`, `Node.js`.
- Interactive skill verification: users can add or remove detected skills directly in the UI.

### ⚖️ Job Description Matching & TF-IDF Cosine Similarity
- Sublinear term-frequency TF-IDF vectorization with English stop-word filtering and unigram/bigram n-grams.
- Cosine similarity between resume and job description term vectors.
- Automated skill gap segmentation:
  - **Matched Skills:** Present in both resume and job description.
  - **Missing Skills:** Explicitly requested by the employer but absent in the resume.
  - **Additional Skills:** Candidate skills that exceed baseline job requirements.
- Importance-weighted keyword gap analysis (High, Medium, Low TF-IDF impact).

### 🎯 Transparent ATS Compatibility Score (0–100)
- Configurable component weights summing to 100%:
  - **Skill Coverage (40% default):** Ratio of matched job skills to total required job skills.
  - **Semantic Similarity (25% default):** Normalized cosine distance between term frequency matrices.
  - **Experience & Projects (20% default):** Depth of practical experience, action verbs, and applied skills.
  - **Education & Background (15% default):** Degree relevance, graduation year, and STEM field alignment.
- Interactive circular gauge visualization (Plotly).
- Explicit mathematical breakdown printed in the UI.

### ✨ Resume Improvement Assistant
- Implements the **Google XYZ formula**: *"Accomplished [X], as measured by [Y], by doing [Z]"*.
- Flags passive phrases (*"worked on"*, *"assisted with"*, *"responsible for"*).
- Converts weak drafts into 3 specialized variations:
  1. **Metric-Focused:** Injects quantifiable placeholders `[X%]`, `[Y ms]`.
  2. **Architecture & Scale:** Highlights concurrency, uptime, and database records.
  3. **Efficiency & Automation:** Focuses on engineering time saved and manual workflow automation.
- Never invents false experiences; uses clear metric brackets.

### 📊 Reports & Local History
- **Downloadable PDF Audit Report:** High-resolution vector PDF generated with `ReportLab` containing scores, pillar breakdowns, skill comparisons, and priority checklists.
- **Downloadable CSV Data:** Tabular breakdown of extracted skills, status, and recommendations.
- **SQLite History:** Local database tracking past scans, timestamps, scores, and target roles with delete/clear controls.

---

## 3. System Architecture

```
┌──────────────────────────────────────┐       ┌──────────────────────────────────────┐
│        Candidate Resume (PDF)        │       │       Job Description (Text)         │
└──────────────────┬───────────────────┘       └──────────────────┬───────────────────┘
                   │                                              │
                   ▼                                              ▼
        [ pdfminer.six Parser ]                      [ Keyword & Requirements Extractor ]
    • Text sanitization & cleaning                  • Degree & experience pattern matching
    • Contact channel extraction (Regex)            • TF-IDF feature extraction (n-grams)
    • Section segmentation (6 sections)                            │
                   │                                              │
                   ▼                                              ▼
        [ Skill Taxonomy Engine ] ◄──────────────────► [ Job Matching Module ]
    • data/skills.json (150+ skills)                • TF-IDF Cosine Similarity
    • Alias resolver (K8s -> Kubernetes)            • Matched, Missing & Extra Skills
    • Boundary regex for C++, C#, .NET              • High/Medium/Low Keyword Gaps
                   │                                              │
                   └──────────────────────┬───────────────────────┘
                                          │
                                          ▼
                             [ Explainable ATS Scorer ]
                         • Skill Coverage          (40%)
                         • Semantic Text Match     (25%)
                         • Projects & Experience   (20%)
                         • Education Alignment     (15%)
                                          │
            ┌─────────────────────────────┼─────────────────────────────┐
            ▼                             ▼                             ▼
   [ Streamlit Dashboard ]      [ ReportLab Exporter ]       [ SQLite Scan Database ]
   • Plotly Circular Gauge      • Professional PDF report    • Timestamped history
   • Category distribution      • Tabular CSV export         • Safe metadata only
   • Priority action checklist  • Instant downloads          • No raw PII stored
```

---

## 4. Explainable ATS Scoring Model

The overall compatibility score is calculated using four distinct pillars:

$$\text{ATS Score} = (S_{\text{skills}} \times W_1) + (S_{\text{similarity}} \times W_2) + (S_{\text{experience}} \times W_3) + (S_{\text{education}} \times W_4)$$

| Pillar | Default Weight | Metric Evaluated | Calculation Rationale |
| :--- | :---: | :--- | :--- |
| **Skill Coverage** | **40%** | $\frac{\text{Matched Skills}}{\text{Total Required Skills}}$ | Evaluates presence of mandatory hard skills & tools |
| **Semantic Similarity** | **25%** | $\frac{\text{Cosine Similarity}}{0.65} \times 100$ | Evaluates vocabulary and technical domain terminology overlap |
| **Experience & Projects** | **20%** | Applied Skills + Action Verbs + Metrics | Evaluates whether skills are applied in concrete projects |
| **Education Relevance** | **15%** | Degree level + STEM Field Alignment | Checks degree alignment against job description requirements |

### Score Band Interpretation:
- 🟢 **85 – 100:** *Exceptional Match* — Excellent alignment across skills, experience, and background.
- 🔵 **70 – 84:** *Strong Match* — Covers core competencies; minor keyword tuning recommended.
- 🟡 **55 – 69:** *Moderate Match* — Baseline foundations present; noticeable missing tools or keywords.
- 🟠 **40 – 54:** *Needs Optimization* — Significant gaps in core skills and terminology.
- 🔴 **0 – 39:** *Low Match* — Substantial mismatch between resume profile and job requirements.

---

## 5. Technology Stack

- **Core Language:** Python 3.10 – 3.13
- **Web UI & Dashboard:** Streamlit 1.30+
- **Machine Learning & NLP:** Scikit-learn (TF-IDF Vectorizer, Cosine Similarity)
- **PDF Extraction:** `pdfminer.six`
- **Visualizations:** Plotly Express & Plotly Graph Objects
- **Document Generation:** `ReportLab` (PDF generation)
- **Data Handling:** Pandas, NumPy
- **Persistence:** SQLite3 (local lightweight relational database)

---

## 6. Project Structure

```
ai-resume-analyzer/
├── app.py                      # Main Streamlit web application & navigation
├── requirements.txt            # Python package dependencies
├── README.md                   # Comprehensive documentation & setup instructions
├── .gitignore                  # Git ignore rules for virtualenvs, caches, databases
├── .env.example                # Example environment variables (optional LLM keys)
│
├── .streamlit/
│   └── config.toml             # Theme configuration (Navy dark theme, port settings)
│
├── assets/
│   └── style.css               # Modern CSS styling (cards, badges, skill tags)
│
├── data/
│   └── skills.json             # Categorized skill taxonomy with 150+ terms
│
├── modules/
│   ├── __init__.py
│   ├── resume_parser.py        # PDF extraction, contact regex, and section segmenter
│   ├── skill_extractor.py      # Skill taxonomy matching, alias resolution, regex
│   ├── job_matcher.py          # TF-IDF vectorizer, cosine similarity, keyword gaps
│   ├── ats_scorer.py           # Multi-pillar explainable ATS scoring engine
│   ├── recommendations.py      # Priority checklist & Google XYZ bullet enhancer
│   ├── report_generator.py     # ReportLab PDF & CSV audit exporter
│   └── database.py             # SQLite history manager
│
├── samples/
│   ├── create_sample_resumes.py # Script generating sample PDF resumes
│   ├── sample_jobs.json        # 4 pre-loaded realistic job descriptions
│   ├── sample_resume_aiml.pdf  # Synthetic sample AI/ML Engineer resume
│   └── sample_resume_swe.pdf   # Synthetic sample Full Stack Engineer resume
│
└── tests/
    ├── __init__.py
    ├── test_parser.py          # Unit tests for PDF parser & contact extraction
    ├── test_matcher.py         # Unit tests for skill extractor & TF-IDF similarity
    ├── test_scorer.py          # Unit tests for ATS scoring engine & weights
    ├── test_recommendations.py # Unit tests for recommendations & bullet enhancer
    ├── test_database.py        # Unit tests for SQLite history logging
    └── test_end_to_end.py      # Complete pipeline integration test
```

---

## 7. Getting Started (Windows & VS Code)

### Prerequisites
- Python 3.10 or higher installed. (Check with `python --version`)
- Visual Studio Code (optional, but recommended).
- Git installed.

### Step-by-Step Installation:

1. **Open PowerShell in your project folder:**
   ```powershell
   cd "c:\Users\bhanu\OneDrive\Desktop\AI resume analyzer"
   ```

2. **Create a virtual environment:**
   ```powershell
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   ```powershell
   .venv\Scripts\Activate.ps1
   ```
   > *Note:* If PowerShell gives an execution policy error, run:
   > `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

4. **Upgrade pip and install dependencies:**
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

5. **Generate sample test resumes (if not already present):**
   ```powershell
   python samples\create_sample_resumes.py
   ```

6. **Start the Streamlit application:**
   ```powershell
   streamlit run app.py
   ```

7. **Access the application:**
   Open your browser to: **`http://localhost:8501`**

---

## 8. Usage Guide

### 1. Home / Dashboard
- View scan statistics, average scores, and how the multi-stage pipeline works.

### 2. Analyze Resume
- **Upload:** Drag & drop your PDF resume, or click one of the quick buttons:
  - 🤖 *Sample AI/ML Resume*
  - 💻 *Sample Full Stack Resume*
- **Verify Skills:** Review extracted skills and add or remove detected badges.
- **Job Description:** Paste your target job description or choose a preset role (*AI/ML, Full Stack, Data Scientist, DevOps*).
- **Run Analysis:** Click **"Run Intelligent ATS Analysis"**.
- **Inspect Results:**
  - View circular ATS compatibility gauge.
  - Review pillar score breakdown and transparent mathematical formula.
  - Inspect matched (green), missing (red), and additional (indigo) skill badges.
  - Download the **Full PDF Audit Report** or **CSV Breakdown**.

### 3. Skills Gap Analysis
- View category-by-category distribution (*Languages, Frameworks, ML/AI, Cloud/DevOps*).
- Inspect top TF-IDF keyword gaps and see which important phrases are missing.
- Review recommended project ideas to naturally bridge missing skills.

### 4. Resume Improvement Assistant
- Paste any draft bullet point or project description.
- Select your engineering specialization.
- Click **"Enhance Bullet Point"** to diagnose passive phrasing and generate 3 quantified Google XYZ variations with metric placeholders.

### 5. Analysis History
- View previous local scans stored in SQLite.
- Track score progression over time.
- Delete individual records or clear scan history.

---

## 9. Running Tests

The application includes a comprehensive unit and integration test suite covering all modules:

```powershell
# Run the entire test suite with unittest discover
python -m unittest discover tests -v
```

Expected output:
```
test_delete_and_clear (test_database.TestDatabase) ... ok
test_save_and_retrieve (test_database.TestDatabase) ... ok
test_complete_workflow (test_end_to_end.TestEndToEndPipeline) ... ok
test_empty_text_similarity (test_matcher.TestJobMatcher) ... ok
test_skill_extraction_aliases_and_symbols (test_matcher.TestJobMatcher) ... ok
test_skill_matching_coverage (test_matcher.TestJobMatcher) ... ok
test_tfidf_similarity_bounds (test_matcher.TestJobMatcher) ... ok
test_extract_contact_info (test_parser.TestResumeParser) ... ok
test_file_validation_empty_bytes (test_parser.TestResumeParser) ... ok
test_file_validation_invalid_extension (test_parser.TestResumeParser) ... ok
test_file_validation_valid_pdf (test_parser.TestResumeParser) ... ok
test_parse_sample_pdf (test_parser.TestResumeParser) ... ok
test_bullet_point_transformation (test_recommendations.TestRecommendations) ... ok
test_section_audit (test_recommendations.TestRecommendations) ... ok
test_custom_weights_normalization (test_scorer.TestATSScorer) ... ok
test_score_bounds_and_structure (test_scorer.TestATSScorer) ... ok

----------------------------------------------------------------------
Ran 16 tests in 0.265s

OK
```

---

## 10. Troubleshooting

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell execution policy restriction | Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` in PowerShell. |
| `Port 8501 is already in use` | Another instance of Streamlit is running | Start on an alternate port: `streamlit run app.py --server.port 8502`. |
| `No extractable text was found in the PDF` | Uploaded PDF is a scanned image or protected | Ensure your PDF contains digital text (highlightable). Scanned image PDFs require OCR. |
| `ModuleNotFoundError: No module named 'reportlab'` | Missing dependency in current python environment | Run `pip install -r requirements.txt` within the active `.venv`. |
| `AttributeError: module 'fitz' not found` | App uses pdfminer.six by default | Our codebase is engineered using `pdfminer.six` directly to eliminate C-library dependency issues. |

---

## 11. Deployment Guide

### Streamlit Community Cloud (Recommended & Free):
1. Push your repository to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI Resume Analyzer"
   git remote add origin https://github.com/your-username/ai-resume-analyzer.git
   git push -u origin main
   ```
2. Navigate to [share.streamlit.io](https://share.streamlit.io/).
3. Connect your GitHub repository.
4. Set Main file path: `app.py`.
5. Click **Deploy!**

---

## 12. Ethical AI & Compliance

- **No Automated Hiring or Rejection:** This application provides advisory diagnostic feedback to help job seekers present their genuine skills effectively. It does not make automated employment decisions.
- **Demographic Agnostic:** Evaluations strictly analyze technical competencies, education, and experience keywords. Demographic traits (race, gender, nationality, age) are never collected or scored.
- **Privacy By Design:** Resumes are processed locally in memory. No resume text, contact details, or candidate data is transmitted to external servers or logged in plain text.

---

## 📜 License
This project is open-source under the MIT License.
Academic evaluation and CSE (AI & ML) project showcase use is welcomed.
