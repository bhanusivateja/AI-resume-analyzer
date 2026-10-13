"""
test_scorer.py - Unit tests for ATSScorer
"""

import unittest
from modules.ats_scorer import ATSScorer


class TestATSScorer(unittest.TestCase):

    def setUp(self):
        self.scorer = ATSScorer()

    def test_score_bounds_and_structure(self):
        match_results = {
            "skill_coverage_pct": 75.0,
            "tfidf_similarity_score": 0.45,
            "matched_skills": ["Python", "FastAPI", "Docker"],
            "total_jd_skills_count": 4,
            "job_requirements": {
                "education_level": ["Bachelor's Degree"]
            }
        }
        sections = {
            "experience": "Developed REST APIs using Python and Docker, optimizing latency by 25%.",
            "projects": "Built FastAPI backend serving 1,000+ users.",
            "education": "Bachelor of Technology in Computer Science, 2024"
        }

        result = self.scorer.calculate_score(match_results, sections)

        self.assertIn("overall_score", result)
        self.assertGreaterEqual(result["overall_score"], 0.0)
        self.assertLessEqual(result["overall_score"], 100.0)
        self.assertIn("breakdown", result)
        self.assertIn("rating", result)
        self.assertIn("disclaimer", result)

    def test_custom_weights_normalization(self):
        custom_weights = {
            "skill_coverage": 50,
            "text_similarity": 50,
            "experience_projects": 0,
            "education": 0
        }
        custom_scorer = ATSScorer(custom_weights)
        self.assertAlmostEqual(custom_scorer.weights["skill_coverage"], 0.5)
        self.assertAlmostEqual(custom_scorer.weights["text_similarity"], 0.5)
        self.assertEqual(custom_scorer.weights["experience_projects"], 0.0)


if __name__ == "__main__":
    unittest.main()
