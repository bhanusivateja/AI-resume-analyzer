"""
test_end_to_end.py - End-to-end integration test for AI Resume Analyzer workflow.
Verifies PDF ingestion -> parsing -> matching -> ATS scoring -> recommendations -> PDF/CSV exports -> SQLite storage.
"""

import os
import unittest
import tempfile
from modules.resume_parser import ResumeParser
from modules.skill_extractor import SkillExtractor
from modules.job_matcher import JobMatcher
from modules.ats_scorer import ATSScorer
from modules.recommendations import RecommendationEngine, ResumeImprovementAssistant
from modules.report_generator import ReportGenerator
from modules.database import DatabaseManager


class TestEndToEndPipeline(unittest.TestCase):

    def setUp(self):
        self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.sample_pdf = os.path.join(self.base_dir, "samples", "sample_resume_aiml.pdf")

        self.sample_jd = """
        Job Title: AI & Machine Learning Engineer
        Responsibilities:
        - Design and build deep learning and NLP models using PyTorch, Transformers, and Scikit-learn.
        - Implement Retrieval-Augmented Generation (RAG) using LangChain and vector databases.
        - Deploy microservices using Docker and FastAPI on AWS.
        - Perform data manipulation with Pandas, NumPy, and SQL.
        Requirements:
        - Bachelor's degree in Computer Science or AI.
        - Experience with Python, Docker, PyTorch, and Git.
        """

    def test_complete_workflow(self):
        # 1. Parsing
        parser = ResumeParser()
        self.assertTrue(os.path.exists(self.sample_pdf))
        parsed = parser.parse(self.sample_pdf, "sample_resume_aiml.pdf")
        self.assertIsNotNone(parsed["cleaned_text"])
        self.assertEqual(parsed["contact_info"]["name"], "Alex Chen")

        # 2. Skill Extraction & Matching
        extractor = SkillExtractor()
        matcher = JobMatcher(extractor)
        match_results = matcher.match(parsed["cleaned_text"], self.sample_jd)

        self.assertGreater(len(match_results["matched_skills"]), 0)
        self.assertGreater(match_results["skill_coverage_pct"], 50.0)
        self.assertGreater(match_results["tfidf_similarity_score"], 0.15)

        # 3. ATS Scoring
        scorer = ATSScorer()
        ats_results = scorer.calculate_score(match_results, parsed["sections"])
        self.assertIn("overall_score", ats_results)
        self.assertGreater(ats_results["overall_score"], 60.0)

        # 4. Recommendations
        rec_engine = RecommendationEngine()
        recs = rec_engine.generate_recommendations(match_results, ats_results, parsed)
        self.assertIsInstance(recs, list)

        # 5. Report Generation (PDF and CSV)
        report_gen = ReportGenerator()
        pdf_bytes = report_gen.generate_pdf_report(
            candidate_name="Alex Chen",
            job_title="AI Engineer",
            ats_results=ats_results,
            match_results=match_results,
            recommendations=recs
        )
        self.assertGreater(len(pdf_bytes), 1000)
        # Verify it starts with PDF magic bytes
        self.assertTrue(pdf_bytes.startswith(b"%PDF"))

        csv_str = report_gen.generate_csv_report(match_results, recs)
        self.assertIn("Skill Matching", csv_str)

        # 6. Database Storage
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            db = DatabaseManager(db_path)
            scan_id = db.save_analysis(
                candidate_name="Alex Chen",
                job_title="AI Engineer",
                overall_score=ats_results["overall_score"],
                rating_label=ats_results["rating"]["label"],
                matched_skills=match_results["matched_skills"],
                missing_skills=match_results["missing_skills"]
            )
            self.assertGreater(scan_id, 0)
            records = db.get_all_analyses()
            self.assertEqual(len(records), 1)


if __name__ == "__main__":
    unittest.main()
