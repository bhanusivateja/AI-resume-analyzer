"""
test_parser.py - Unit tests for ResumeParser
"""

import os
import unittest
from modules.resume_parser import ResumeParser, ResumeParsingError


class TestResumeParser(unittest.TestCase):

    def setUp(self):
        self.parser = ResumeParser()
        self.samples_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")
        self.sample_aiml = os.path.join(self.samples_dir, "sample_resume_aiml.pdf")

    def test_file_validation_valid_pdf(self):
        with open(self.sample_aiml, "rb") as f:
            content = f.read()
        valid, err = self.parser.validate_file(content, "sample.pdf")
        self.assertTrue(valid)
        self.assertIsNone(err)

    def test_file_validation_invalid_extension(self):
        valid, err = self.parser.validate_file(b"test data", "resume.docx")
        self.assertFalse(valid)
        self.assertIn("Only PDF files are supported", err)

    def test_file_validation_empty_bytes(self):
        valid, err = self.parser.validate_file(b"", "resume.pdf")
        self.assertFalse(valid)
        self.assertIn("empty", err.lower())

    def test_extract_contact_info(self):
        sample_text = """
        John Doe
        Software Engineer
        Email: john.doe@example.com | Phone: +1 555-123-4567
        LinkedIn: linkedin.com/in/johndoe | GitHub: github.com/johndoe
        """
        contacts = self.parser.extract_contact_info(sample_text)
        self.assertEqual(contacts["email"], "john.doe@example.com")
        self.assertIn("555-123-4567", contacts["phone"])
        self.assertIn("linkedin.com/in/johndoe", contacts["linkedin"])
        self.assertIn("github.com/johndoe", contacts["github"])
        self.assertEqual(contacts["name"], "John Doe")

    def test_parse_sample_pdf(self):
        result = self.parser.parse(self.sample_aiml, "sample_resume_aiml.pdf")
        self.assertIn("raw_text", result)
        self.assertIn("contact_info", result)
        self.assertIn("sections", result)
        self.assertGreater(result["metadata"]["word_count"], 50)
        self.assertEqual(result["contact_info"]["email"], "alex.chen@example.com")


if __name__ == "__main__":
    unittest.main()
