"""
ats_scorer.py - Transparent, Explainable ATS-Style Compatibility Scoring Engine
Computes a normalized 0-100 score across 4 configurable weighted pillars:
1. Skill Coverage (default: 40%)
2. Text Semantic Similarity (default: 25%)
3. Experience & Project Alignment (default: 20%)
4. Education & Qualifications Match (default: 15%)
"""

import re
from typing import Dict, Any, List, Optional, Tuple


class ATSScorer:
    """Calculates an explainable ATS-style compatibility score with clear component weights."""

    DEFAULT_WEIGHTS = {
        "skill_coverage": 0.40,
        "text_similarity": 0.25,
        "experience_projects": 0.20,
        "education": 0.15,
    }

    ACTION_VERBS = [
        "built", "developed", "designed", "architected", "implemented", "deployed",
        "engineered", "optimized", "spearheaded", "orchestrated", "automated",
        "reduced", "increased", "scaled", "created", "integrated", "managed", "led"
    ]

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """Initialize with custom weights or defaults. Weights are normalized to sum to 1.0."""
        self.weights = weights or dict(self.DEFAULT_WEIGHTS)
        self._normalize_weights()

    def _normalize_weights(self) -> None:
        """Ensure all weights sum to 1.0 (100%)."""
        total = sum(self.weights.values())
        if total <= 0:
            self.weights = dict(self.DEFAULT_WEIGHTS)
            total = 1.0
        self.weights = {k: v / total for k, v in self.weights.items()}

    def evaluate_experience_projects(
        self,
        sections: Dict[str, str],
        matched_skills: List[str]
    ) -> Tuple[float, str]:
        """
        Evaluate practical experience and project depth:
        - Checks presence of experience / project sections
        - Checks if matched skills appear within experience or project sections (applied skills)
        - Checks for action verbs and quantified impact metrics
        """
        exp_text = sections.get("experience", "").lower()
        proj_text = sections.get("projects", "").lower()
        combined_text = f"{exp_text}\n{proj_text}"

        score = 0.0
        explanations = []

        if not exp_text and not proj_text:
            return 20.0, "Experience or Project sections were not distinctly detected."

        # Base presence score
        has_exp = len(exp_text.split()) > 30
        has_proj = len(proj_text.split()) > 30

        if has_exp and has_proj:
            score += 35.0
            explanations.append("Both Experience and Projects sections are well populated.")
        elif has_exp or has_proj:
            score += 25.0
            explanations.append("Either Experience or Projects section is populated.")

        # Check applied skills in projects/experience
        if matched_skills:
            applied_count = sum(1 for s in matched_skills if s.lower() in combined_text)
            applied_ratio = applied_count / len(matched_skills)
            applied_score = min(40.0, applied_ratio * 40.0)
            score += applied_score
            explanations.append(f"{applied_count}/{len(matched_skills)} required skills demonstrated in experience/projects.")
        else:
            score += 20.0

        # Action verbs & impact quantification checks
        action_verb_count = sum(1 for v in self.ACTION_VERBS if re.search(rf"\b{v}\b", combined_text))
        has_metrics = bool(re.search(r"\b(?:\d+%(?:\s+increase|\s+reduction)?|\$\d+|\d+\+?\s*(?:users|clients|ms|requests))\b", combined_text))

        if action_verb_count >= 4:
            score += 15.0
            explanations.append("Strong use of action-oriented verbs.")
        elif action_verb_count >= 1:
            score += 8.0

        if has_metrics:
            score += 10.0
            explanations.append("Includes measurable metrics / quantified achievements.")
        else:
            explanations.append("Lacks quantified impact numbers (percentages, metrics).")

        final_score = min(100.0, max(0.0, score))
        return round(final_score, 1), " ".join(explanations)

    def evaluate_education(
        self,
        sections: Dict[str, str],
        job_requirements: Dict[str, Any]
    ) -> Tuple[float, str]:
        """
        Evaluate education alignment against job requirements.
        """
        edu_text = sections.get("education", "").lower()
        required_degrees = job_requirements.get("education_level", [])

        if not edu_text:
            return 40.0, "Education section not distinctly identified; partial default score applied."

        score = 50.0  # Base score for having an education section
        explanations = ["Education section is present."]

        # Check for degree mentions in education section
        has_degree = bool(re.search(
            r"\b(?:b\.?tech|b\.?e|bachelor|b\.?s|m\.?tech|m\.?e|master|m\.?s|m\.?b\.?a|ph\.?d|degree)\b",
            edu_text
        ))

        if has_degree:
            score += 25.0
            explanations.append("Recognized degree detected.")

        # Check stem field
        has_stem = bool(re.search(
            r"\b(?:computer\s+science|engineering|information\s+technology|data|mathematics|ai|ml)\b",
            edu_text
        ))
        if has_stem:
            score += 15.0
            explanations.append("Relevant STEM / Computer Science field specified.")

        # Alignment with JD requirements
        if required_degrees:
            matched_req = False
            for req in required_degrees:
                if (
                    ("bachelor" in req.lower() and "bachelor" in edu_text or "b.tech" in edu_text or "b.e" in edu_text or "b.s" in edu_text)
                    or ("master" in req.lower() and "master" in edu_text or "m.s" in edu_text or "m.tech" in edu_text)
                    or ("ph.d" in req.lower() and "ph.d" in edu_text or "doctorate" in edu_text)
                ):
                    matched_req = True
                    break

            if matched_req:
                score += 10.0
                explanations.append("Matches degree requirement specified in job description.")
        else:
            score += 10.0

        final_score = min(100.0, max(0.0, score))
        return round(final_score, 1), " ".join(explanations)

    def get_rating_category(self, score: float) -> Dict[str, str]:
        """Convert score into user-friendly status badge and description."""
        if score >= 85:
            return {
                "label": "Exceptional Match",
                "color": "#10B981",  # emerald
                "badge": "🟢 High Compatibility",
                "summary": "Outstanding alignment with job requirements across skills, experience, and background."
            }
        elif score >= 70:
            return {
                "label": "Strong Match",
                "color": "#3B82F6",  # blue
                "badge": "🔵 Strong Compatibility",
                "summary": "Great match with the core qualifications. Minor keyword optimizations will maximize ATS pass rates."
            }
        elif score >= 55:
            return {
                "label": "Moderate Match",
                "color": "#F59E0B",  # amber
                "badge": "🟡 Moderate Compatibility",
                "summary": "Covers essential foundations, but has notable missing skills or keyword gaps that require attention."
            }
        elif score >= 40:
            return {
                "label": "Needs Optimization",
                "color": "#F97316",  # orange
                "badge": "🟠 Significant Gaps",
                "summary": "Key technical competencies and domain keywords from the job description are missing."
            }
        else:
            return {
                "label": "Low Compatibility",
                "color": "#EF4444",  # red
                "badge": "🔴 Low Compatibility",
                "summary": "Substantial gap between resume profile and job requirements. Significant revision advised."
            }

    def calculate_score(
        self,
        match_results: Dict[str, Any],
        resume_sections: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Calculate transparent weighted compatibility score:
        Returns component scores, final weighted score, and detailed rationale.
        """
        # 1. Skill Coverage (0 - 100)
        skill_coverage_score = float(match_results.get("skill_coverage_pct", 0.0))
        skill_exp = f"{len(match_results.get('matched_skills', []))} of {match_results.get('total_jd_skills_count', 0)} required skills matched."

        # 2. Text Similarity (0 - 100)
        # Cosine similarity on TF-IDF vectors naturally ranges 0.15 - 0.75 for good documents
        # We scale appropriately: a raw cosine similarity of 0.50+ represents very high alignment
        raw_cosine = match_results.get("tfidf_similarity_score", 0.0)
        scaled_similarity = min(100.0, (raw_cosine / 0.65) * 100.0) if raw_cosine > 0 else 0.0
        scaled_similarity = round(scaled_similarity, 1)
        sim_exp = f"Raw TF-IDF cosine similarity of {raw_cosine:.3f} mapped across term vector overlap."

        # 3. Experience & Projects Alignment (0 - 100)
        matched_skills = match_results.get("matched_skills", [])
        exp_score, exp_reasoning = self.evaluate_experience_projects(resume_sections, matched_skills)

        # 4. Education Alignment (0 - 100)
        job_reqs = match_results.get("job_requirements", {})
        edu_score, edu_reasoning = self.evaluate_education(resume_sections, job_reqs)

        # Calculate weighted sum
        w_skills = self.weights.get("skill_coverage", 0.40)
        w_sim = self.weights.get("text_similarity", 0.25)
        w_exp = self.weights.get("experience_projects", 0.20)
        w_edu = self.weights.get("education", 0.15)

        overall_score = (
            (skill_coverage_score * w_skills) +
            (scaled_similarity * w_sim) +
            (exp_score * w_exp) +
            (edu_score * w_edu)
        )
        overall_score = max(0.0, min(100.0, round(overall_score, 1)))

        rating = self.get_rating_category(overall_score)

        breakdown = {
            "skill_coverage": {
                "name": "Skill Coverage",
                "raw_score": skill_coverage_score,
                "weight": round(w_skills * 100, 1),
                "weighted_score": round(skill_coverage_score * w_skills, 1),
                "explanation": skill_exp
            },
            "text_similarity": {
                "name": "Semantic Text Similarity",
                "raw_score": scaled_similarity,
                "weight": round(w_sim * 100, 1),
                "weighted_score": round(scaled_similarity * w_sim, 1),
                "explanation": sim_exp
            },
            "experience_projects": {
                "name": "Experience & Projects",
                "raw_score": exp_score,
                "weight": round(w_exp * 100, 1),
                "weighted_score": round(exp_score * w_exp, 1),
                "explanation": exp_reasoning
            },
            "education": {
                "name": "Education & Background",
                "raw_score": edu_score,
                "weight": round(w_edu * 100, 1),
                "weighted_score": round(edu_score * w_edu, 1),
                "explanation": edu_reasoning
            }
        }

        formula_explanation = (
            f"Compatibility Score = ({skill_coverage_score} × {w_skills:.2f}) + "
            f"({scaled_similarity} × {w_sim:.2f}) + ({exp_score} × {w_exp:.2f}) + "
            f"({edu_score} × {w_edu:.2f}) = {overall_score}/100"
        )

        return {
            "overall_score": overall_score,
            "rating": rating,
            "breakdown": breakdown,
            "formula_explanation": formula_explanation,
            "disclaimer": (
                "Notice: This is an estimated compatibility score calculated using transparent "
                "NLP algorithms (TF-IDF vectorization, keyword coverage, and section heuristics). "
                "It does not represent proprietary scoring from any specific commercial ATS vendor, "
                "and does not predict employment or hiring decisions."
            )
        }
