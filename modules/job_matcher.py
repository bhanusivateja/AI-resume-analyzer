"""
job_matcher.py - Job Description Matcher using TF-IDF, Cosine Similarity, and Keyword Analysis
Extracts requirements, compares skills, computes semantic similarity, and identifies critical keyword gaps.
"""

import re
from typing import Dict, List, Set, Any, Tuple, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .skill_extractor import SkillExtractor


class JobMatcher:
    """Matches resume text and skills against job description text and requirements."""

    def __init__(self, skill_extractor: Optional[SkillExtractor] = None):
        self.skill_extractor = skill_extractor or SkillExtractor()

    def preprocess_text(self, text: str) -> str:
        """Clean and normalize text for TF-IDF vectorization."""
        if not text:
            return ""
        # Lowercase
        cleaned = text.lower()
        # Keep alphanumeric, basic programming terms
        cleaned = re.sub(r"[^\w\s\+\#\.]", " ", cleaned)
        # Collapse whitespace
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def compute_tfidf_similarity(self, resume_text: str, jd_text: str) -> float:
        """
        Compute TF-IDF cosine similarity between resume and job description.
        Returns a float between 0.0 and 1.0.
        """
        clean_resume = self.preprocess_text(resume_text)
        clean_jd = self.preprocess_text(jd_text)

        if not clean_resume or not clean_jd:
            return 0.0

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                max_features=2500,
                sublinear_tf=True
            )
            tfidf_matrix = vectorizer.fit_transform([clean_resume, clean_jd])
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            # Clip between 0.0 and 1.0
            return max(0.0, min(1.0, float(similarity)))
        except Exception:
            return 0.0

    def extract_job_requirements(self, jd_text: str) -> Dict[str, Any]:
        """Extract experience years, degree requirements, and key responsibilities from JD."""
        requirements: Dict[str, Any] = {
            "experience_years": None,
            "education_level": [],
            "key_phrases": []
        }

        # Experience pattern: e.g. "3+ years", "2-5 years", "minimum 4 years"
        exp_match = re.search(
            r"(?:minimum|at least)?\s*(\d+(?:\+|-?\d*)?)\s*(?:to\s*\d+\s*)?(?:years?|yrs?)(?:\s+of)?(?:\s+experience)?",
            jd_text,
            re.IGNORECASE
        )
        if exp_match:
            requirements["experience_years"] = exp_match.group(0).strip()

        # Education degree pattern
        edu_patterns = [
            (r"\b(?:b\.?tech|b\.?e|bachelor(?:'s)?(?:\s+degree)?|b\.?s\.?)\b", "Bachelor's Degree"),
            (r"\b(?:m\.?tech|m\.?e|master(?:'s)?(?:\s+degree)?|m\.?s\.?|m\.?b\.?a)\b", "Master's Degree"),
            (r"\b(?:ph\.?d|doctorate)\b", "Ph.D. / Doctorate"),
            (r"\b(?:computer\s+science|information\s+technology|data\s+science|engineering)\b", "CS/Stem Discipline")
        ]
        for pattern, label in edu_patterns:
            if re.search(pattern, jd_text, re.IGNORECASE) and label not in requirements["education_level"]:
                requirements["education_level"].append(label)

        return requirements

    def analyze_keyword_gaps(self, resume_text: str, jd_text: str, top_n: int = 25) -> List[Dict[str, Any]]:
        """
        Extract top TF-IDF keywords from Job Description and check their presence in the resume.
        Returns list of keyword gap dicts with importance scores.
        """
        clean_resume = self.preprocess_text(resume_text)
        clean_jd = self.preprocess_text(jd_text)

        if not clean_resume or not clean_jd:
            return []

        try:
            vectorizer = TfidfVectorizer(
                stop_words="english",
                ngram_range=(1, 2),
                token_pattern=r"(?u)\b[a-zA-Z0-9_\+\#]{2,}\b"
            )
            jd_matrix = vectorizer.fit_transform([clean_jd])
            feature_names = vectorizer.get_feature_names_out()
            scores = jd_matrix.toarray()[0]

            # Sort keywords by TF-IDF score in JD
            keyword_scores = list(zip(feature_names, scores))
            keyword_scores.sort(key=lambda x: x[1], reverse=True)

            gaps = []
            resume_words_set = set(clean_resume.split())

            for kw, score in keyword_scores[:top_n]:
                # Check if multi-word or single-word keyword is in resume
                is_in_resume = kw in clean_resume if " " in kw else kw in resume_words_set

                # Determine importance level
                if score >= 0.25:
                    importance = "High"
                elif score >= 0.15:
                    importance = "Medium"
                else:
                    importance = "Low"

                gaps.append({
                    "keyword": kw,
                    "score": round(float(score), 3),
                    "found_in_resume": is_in_resume,
                    "importance": importance
                })

            return gaps
        except Exception:
            return []

    def match(
        self,
        resume_text: str,
        jd_text: str,
        resume_skills_override: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Perform complete matching between resume and job description:
        - TF-IDF Cosine Similarity
        - Skill Matching (matched, missing, additional)
        - Keyword Gaps
        - Job Requirements
        """
        # Extract skills from both texts
        if resume_skills_override is not None:
            resume_skills = set(resume_skills_override)
            # Categorize the override skills
            resume_skill_data = {
                "skills": sorted(list(resume_skills)),
                "categorized": {},
                "count": len(resume_skills)
            }
        else:
            resume_skill_data = self.skill_extractor.extract_skills_from_text(resume_text)
            resume_skills = set(resume_skill_data["skills"])

        jd_skill_data = self.skill_extractor.extract_skills_from_text(jd_text)
        jd_skills = set(jd_skill_data["skills"])

        # Skill overlaps
        matched_skills = sorted(list(resume_skills.intersection(jd_skills)))
        missing_skills = sorted(list(jd_skills.difference(resume_skills)))
        additional_skills = sorted(list(resume_skills.difference(jd_skills)))

        total_jd_skills = len(jd_skills)
        skill_coverage_pct = round((len(matched_skills) / total_jd_skills * 100), 1) if total_jd_skills > 0 else 100.0

        # TF-IDF similarity
        tfidf_sim = self.compute_tfidf_similarity(resume_text, jd_text)
        tfidf_similarity_pct = round(tfidf_sim * 100, 1)

        # Keyword gaps
        keyword_gaps = self.analyze_keyword_gaps(resume_text, jd_text)

        # Job requirements
        requirements = self.extract_job_requirements(jd_text)

        return {
            "tfidf_similarity_score": tfidf_sim,
            "tfidf_similarity_pct": tfidf_similarity_pct,
            "skill_coverage_pct": skill_coverage_pct,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "additional_skills": additional_skills,
            "total_jd_skills_count": total_jd_skills,
            "total_resume_skills_count": len(resume_skills),
            "resume_skills_categorized": resume_skill_data.get("categorized", {}),
            "jd_skills_categorized": jd_skill_data.get("categorized", {}),
            "keyword_gaps": keyword_gaps,
            "job_requirements": requirements
        }
