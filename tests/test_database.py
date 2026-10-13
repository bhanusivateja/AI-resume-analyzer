"""
test_database.py - Unit tests for SQLite DatabaseManager
"""

import os
import unittest
import tempfile
from modules.database import DatabaseManager


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_history.db")
        self.db = DatabaseManager(self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_and_retrieve(self):
        scan_id = self.db.save_analysis(
            candidate_name="Alex Chen",
            job_title="AI Engineer",
            overall_score=85.5,
            rating_label="Exceptional Match",
            matched_skills=["Python", "PyTorch"],
            missing_skills=["Kubernetes"]
        )
        self.assertGreater(scan_id, 0)

        records = self.db.get_all_analyses()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["candidate_name"], "Alex Chen")
        self.assertAlmostEqual(records[0]["overall_score"], 85.5)

    def test_delete_and_clear(self):
        scan_id1 = self.db.save_analysis("User1", "SWE", 70.0, "Strong", ["Python"], ["Go"])
        scan_id2 = self.db.save_analysis("User2", "SWE", 60.0, "Moderate", ["Python"], ["Java"])

        self.assertEqual(len(self.db.get_all_analyses()), 2)
        self.db.delete_analysis(scan_id1)
        self.assertEqual(len(self.db.get_all_analyses()), 1)

        self.db.clear_all()
        self.assertEqual(len(self.db.get_all_analyses()), 0)


if __name__ == "__main__":
    unittest.main()
