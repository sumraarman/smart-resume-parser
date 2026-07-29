"""
Unit tests for database.py module.
"""

import os
import shutil
import tempfile
import unittest
from database import ResumeDatabase


class TestDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_file = os.path.join(self.temp_dir, "test_resumes.db")
        self.db = ResumeDatabase(db_path=self.db_file)

    def tearDown(self):
        # Ignore errors on Windows if SQLite file lock takes a moment to release
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_save_and_retrieve_candidate(self):
        candidate_data = {
            "name": "Test Candidate",
            "email": "test@example.com",
            "phone": "+1 999 888 7777",
            "skills": ["Python", "Docker"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": []
        }

        saved = self.db.save_candidate(candidate_data, score=85, raw_text="Test raw text")
        self.assertTrue(saved)

        cands = self.db.get_all_candidates()
        self.assertEqual(len(cands), 1)
        self.assertEqual(cands[0]["name"], "Test Candidate")
        self.assertEqual(cands[0]["score"], 85)

    def test_search_candidate(self):
        candidate_data = {
            "name": "Bob Builder",
            "email": "bob@builder.com",
            "skills": ["Python", "Kubernetes"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": []
        }
        self.db.save_candidate(candidate_data, score=90)

        results = self.db.search_candidates(query="Bob")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["name"], "Bob Builder")

        results_skill = self.db.search_candidates(query="Kubernetes")
        self.assertEqual(len(results_skill), 1)

    def test_delete_candidate(self):
        candidate_data = {
            "name": "Charlie Brown",
            "email": "charlie@peanuts.com",
            "skills": ["Java"],
            "education": [],
            "experience": [],
            "projects": [],
            "certifications": []
        }
        self.db.save_candidate(candidate_data, score=70)
        cands = self.db.get_all_candidates()
        cand_id = cands[0]["id"]

        deleted = self.db.delete_candidate(cand_id)
        self.assertTrue(deleted)

        cands_after = self.db.get_all_candidates()
        self.assertEqual(len(cands_after), 0)


if __name__ == "__main__":
    unittest.main()
