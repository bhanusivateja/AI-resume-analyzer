"""
create_sample_resumes.py - Generates synthetic sample PDF resumes for testing and demonstrations.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable


def build_resume_pdf(filepath: str, name: str, title: str, email: str, phone: str,
                     linkedin: str, github: str, summary: str, skills_dict: dict,
                     experience: list, projects: list, education: list, certs: list):
    doc = SimpleDocTemplate(
        filepath,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    name_style = ParagraphStyle(
        "Name", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=20, leading=24,
        textColor=colors.HexColor("#0F172A")
    )
    role_style = ParagraphStyle(
        "Role", parent=styles["Normal"],
        fontName="Helvetica", fontSize=11, leading=14,
        textColor=colors.HexColor("#4F46E5")
    )
    contact_style = ParagraphStyle(
        "Contact", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=colors.HexColor("#475569")
    )
    h2_style = ParagraphStyle(
        "H2", parent=styles["Normal"],
        fontName="Helvetica-Bold", fontSize=11, leading=15,
        textColor=colors.HexColor("#1E293B"), spaceBefore=8, spaceAfter=3
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        textColor=colors.HexColor("#334155")
    )
    bullet_style = ParagraphStyle(
        "Bullet", parent=styles["Normal"],
        fontName="Helvetica", fontSize=8.5, leading=12,
        leftIndent=12, textColor=colors.HexColor("#334155")
    )

    story = []

    # Header
    story.append(Paragraph(name, name_style))
    story.append(Paragraph(title, role_style))
    contact_text = f"Email: {email} &nbsp;|&nbsp; Phone: {phone} &nbsp;|&nbsp; LinkedIn: {linkedin} &nbsp;|&nbsp; GitHub: {github}"
    story.append(Paragraph(contact_text, contact_style))
    story.append(Spacer(1, 4))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1"), spaceAfter=6))

    # Summary
    story.append(Paragraph("Professional Summary", h2_style))
    story.append(Paragraph(summary, body_style))
    story.append(Spacer(1, 4))

    # Skills
    story.append(Paragraph("Technical Skills", h2_style))
    for cat, skl_list in skills_dict.items():
        skl_str = f"<b>{cat}:</b> {', '.join(skl_list)}"
        story.append(Paragraph(skl_str, body_style))
    story.append(Spacer(1, 4))

    # Experience
    if experience:
        story.append(Paragraph("Work Experience & Internships", h2_style))
        for exp in experience:
            exp_header = f"<b>{exp['role']}</b> – <i>{exp['company']}</i> ({exp['duration']})"
            story.append(Paragraph(exp_header, body_style))
            for bullet in exp['bullets']:
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 3))

    # Projects
    if projects:
        story.append(Paragraph("Key Technical Projects", h2_style))
        for proj in projects:
            p_head = f"<b>{proj['name']}</b> | <i>{proj['tech']}</i>"
            story.append(Paragraph(p_head, body_style))
            for b in proj['bullets']:
                story.append(Paragraph(f"• {b}", bullet_style))
            story.append(Spacer(1, 3))

    # Education
    story.append(Paragraph("Education", h2_style))
    for edu in education:
        edu_str = f"<b>{edu['degree']}</b>, {edu['institution']} ({edu['year']}) – GPA: {edu['gpa']}"
        story.append(Paragraph(edu_str, body_style))
    story.append(Spacer(1, 4))

    # Certifications
    if certs:
        story.append(Paragraph("Certifications & Achievements", h2_style))
        for c in certs:
            story.append(Paragraph(f"• {c}", bullet_style))

    doc.build(story)
    print(f"Generated: {filepath}")


if __name__ == "__main__":
    out_dir = os.path.dirname(os.path.abspath(__file__))

    # 1. AI/ML Engineer Resume
    build_resume_pdf(
        filepath=os.path.join(out_dir, "sample_resume_aiml.pdf"),
        name="Alex Chen",
        title="AI & Machine Learning Engineer",
        email="alex.chen@example.com",
        phone="+1 (555) 234-5678",
        linkedin="linkedin.com/in/alexchen-ai",
        github="github.com/alexchen-dev",
        summary="Results-driven Machine Learning Engineer with a solid foundation in Deep Learning, Natural Language Processing, and MLOps. Experienced in building Retrieval-Augmented Generation (RAG) systems and deploying scalable PyTorch models using Docker and FastAPI.",
        skills_dict={
            "Programming Languages": ["Python", "SQL", "C++", "Bash"],
            "AI / Machine Learning": ["PyTorch", "TensorFlow", "Scikit-learn", "Hugging Face", "Transformers", "NLP", "LangChain", "Pandas", "NumPy", "OpenCV"],
            "MLOps & Cloud": ["Docker", "MLflow", "AWS", "Git", "GitHub Actions", "CI/CD"],
            "Databases & Frameworks": ["PostgreSQL", "FastAPI", "Redis"]
        },
        experience=[
            {
                "role": "Machine Learning Intern",
                "company": "Cognitive AI Solutions",
                "duration": "May 2025 – August 2025",
                "bullets": [
                    "Engineered and fine-tuned BERT-based NLP models for document classification, achieving 93.4% accuracy across 50,000 corporate records.",
                    "Built high-throughput inference APIs using FastAPI and Docker, reducing average response latency by 32% (under 80ms).",
                    "Automated model training pipelines using MLflow and GitHub Actions, cutting continuous retraining cycle time by 4 hours weekly."
                ]
            }
        ],
        projects=[
            {
                "name": "Neural RAG Knowledge Assistant",
                "tech": "Python, LangChain, PyTorch, FAISS, FastAPI, Docker",
                "bullets": [
                    "Architected an enterprise question-answering pipeline using LangChain, Hugging Face embeddings, and FAISS vector database.",
                    "Deployed containerized microservice on AWS EC2 handling 1,500+ daily queries with sub-second retrieval times.",
                    "Implemented semantic chunking and reranking, improving document retrieval precision by 24% over baseline BM25."
                ]
            },
            {
                "name": "Autonomous Vision Defect Detector",
                "tech": "PyTorch, OpenCV, Scikit-learn, Matplotlib",
                "bullets": [
                    "Trained a convolutional neural network (CNN) for surface anomaly detection, achieving a 0.96 F1-score on an industrial benchmark dataset.",
                    "Integrated OpenCV pre-processing filters and automated evaluation scripts with detailed confusion matrices."
                ]
            }
        ],
        education=[
            {
                "degree": "Bachelor of Technology in Computer Science (AI & ML)",
                "institution": "Apex Institute of Technology",
                "year": "2022 - 2026",
                "gpa": "3.85 / 4.0"
            }
        ],
        certs=[
            "DeepLearning.AI Deep Learning Specialization (Coursera)",
            "AWS Certified Cloud Practitioner (Amazon Web Services)",
            "Kaggle Competitions Master – Top 5% in Tabular ML Hackathons"
        ]
    )

    # 2. Full Stack Software Engineer Resume
    build_resume_pdf(
        filepath=os.path.join(out_dir, "sample_resume_swe.pdf"),
        name="Jordan Miller",
        title="Full Stack Software Engineer",
        email="jordan.miller@example.com",
        phone="+1 (555) 876-5432",
        linkedin="linkedin.com/in/jordanmiller-dev",
        github="github.com/jordanm-code",
        summary="Innovative Full Stack Software Developer with 2+ years of hands-on experience building production web applications using React, TypeScript, Node.js, and Python. Passionate about Clean Architecture, Test-Driven Development, and microservices.",
        skills_dict={
            "Programming Languages": ["JavaScript", "TypeScript", "Python", "SQL", "HTML5", "CSS3"],
            "Frontend & Web": ["React", "Next.js", "Tailwind CSS", "Redux", "REST API"],
            "Backend & Databases": ["Node.js", "Express.js", "FastAPI", "PostgreSQL", "MongoDB", "Redis"],
            "DevOps & Tools": ["Docker", "Git", "GitHub Actions", "CI/CD", "AWS", "Jira", "Jest", "PyTest"]
        },
        experience=[
            {
                "role": "Full Stack Developer",
                "company": "Apex Dynamics Web Systems",
                "duration": "June 2024 – Present",
                "bullets": [
                    "Engineered modern web applications with React, Next.js, and TypeScript, serving 45,000+ monthly active users.",
                    "Designed and maintained RESTful APIs in Node.js and PostgreSQL, optimizing SQL queries to improve response times by 40%.",
                    "Built automated CI/CD deployment pipelines using GitHub Actions and Docker, reducing deployment failure rate to under 1%."
                ]
            }
        ],
        projects=[
            {
                "name": "Cloud Workspace Collaboration Platform",
                "tech": "React, TypeScript, FastAPI, PostgreSQL, Redis, Docker",
                "bullets": [
                    "Developed real-time collaborative document editing tool with WebSockets and Redis Pub/Sub.",
                    "Constructed secure role-based access control (RBAC) and JWT authentication, passing security audits with zero vulnerabilities."
                ]
            }
        ],
        education=[
            {
                "degree": "Bachelor of Science in Computer Science",
                "institution": "State University of Science & Technology",
                "year": "2021 - 2025",
                "gpa": "3.8 / 4.0"
            }
        ],
        certs=[
            "Meta Certified Front-End Developer",
            "HashiCorp Terraform Associate (003)"
        ]
    )
