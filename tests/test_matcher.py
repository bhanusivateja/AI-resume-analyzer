"""
test_matcher.py - Unit tests for JobMatcher and SkillExtractor
"""

import unittest
from modules.skill_extractor import SkillExtractor
from modules.job_matcher import JobMatcher


class TestJobMatcher(unittest.TestCase):

    def setUp(self):
        self.extractor = SkillExtractor()
        self.matcher = JobMatcher(self.extractor)

    def test_skill_extraction_aliases_and_symbols(self):
        sample_text = "Proficient in Python, C++, React.js, and K8s. Familiar with AWS and PostgreSQL."
        result = self.extractor.extract_skills_from_text(sample_text)
        skills = result["skills"]

        self.assertIn("Python", skills)
        self.assertIn("C++", skills)
        self.assertIn("React", skills)        # Normalized from React.js
        self.assertIn("Kubernetes", skills)   # Normalized from K8s
        self.assertIn("AWS", skills)
        self.assertIn("PostgreSQL", skills)

    def test_tfidf_similarity_bounds(self):
        text_a = "Senior Python engineer building microservices with Docker and FastAPI."
        text_b = "Looking for a Python software engineer experienced in FastAPI microservices."
        sim = self.matcher.compute_tfidf_similarity(text_a, text_b)

        self.assertGreaterEqual(sim, 0.0)
        self.assertLessEqual(sim, 1.0)
        self.assertGreater(sim, 0.1)

    def test_empty_text_similarity(self):
        sim = self.matcher.compute_tfidf_similarity("", "Some job text")
        self.assertEqual(sim, 0.0)

    def test_skill_matching_coverage(self):
        resume_text = "Experienced in Python, Docker, and SQL."
        jd_text = "Requirements: Python, Docker, SQL, Kubernetes, and AWS."

        match = self.matcher.match(resume_text, jd_text)
        self.assertIn("Python", match["matched_skills"])
        self.assertIn("Docker", match["matched_skills"])
        self.assertIn("Kubernetes", match["missing_skills"])
        self.assertIn("AWS", match["missing_skills"])
        self.assertAlmostEqual(match["skill_coverage_pct"], 60.0, places=1)


if __name__ == "__main__":
    unittest.main()
