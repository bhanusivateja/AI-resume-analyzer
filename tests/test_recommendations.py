"""
test_recommendations.py - Unit tests for RecommendationEngine and ResumeImprovementAssistant
"""

import unittest
from modules.recommendations import RecommendationEngine, ResumeImprovementAssistant


class TestRecommendations(unittest.TestCase):

    def setUp(self):
        self.rec_engine = RecommendationEngine()
        self.assistant = ResumeImprovementAssistant()

    def test_section_audit(self):
        sections = {
            "summary": "Experienced engineer.",
            "skills": "Python, SQL, Docker, AWS, React",
            "experience": "Developed web applications for enterprise clients for 2 years.",
            "education": "B.Tech in Computer Science",
            "projects": "Built an intelligent recommendation system with Python.",
            "certifications": "AWS Certified"
        }
        contacts = {"email": "test@example.com", "phone": "1234567890", "linkedin": "linkedin.com/in/test", "github": None, "portfolio": None}

        audit = self.rec_engine.audit_sections(sections, contacts)
        self.assertIn("sections", audit)
        self.assertIn("contact_score_pct", audit)
        self.assertIn("missing_contacts", audit)
        self.assertIn("github", audit["missing_contacts"])

    def test_bullet_point_transformation(self):
        weak_bullet = "worked on building web services using Python"
        result = self.assistant.enhance_bullet(weak_bullet)

        self.assertIn("suggestions", result)
        self.assertEqual(len(result["suggestions"]), 3)
        # Should detect weakness
        self.assertGreater(len(result["issues"]), 0)
        # Transformed text should not start with 'worked on'
        for sug in result["suggestions"]:
            self.assertFalse(sug["text"].lower().startswith("worked on"))
            self.assertIn("[", sug["text"])  # Contains placeholder


if __name__ == "__main__":
    unittest.main()
