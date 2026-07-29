"""
Unit tests for scoring.py module.
"""

import unittest
from scoring import ResumeScorer, JobDescriptionMatcher, ResumeSummarizer


class TestScoring(unittest.TestCase):

    def test_resume_scorer(self):
        sample_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "phone": "+1 555-1234",
            "linkedin": "https://linkedin.com/in/janedoe",
            "github": "https://github.com/janedoe",
            "skills": ["Python", "Java", "SQL", "React", "Docker", "AWS"],
            "education": [{"degree": "B.Tech"}],
            "experience": [{"company": "Acme", "title": "Developer"}],
            "projects": [{"title": "Project A"}],
            "certifications": ["AWS Certified"]
        }

        result = ResumeScorer.calculate_score(sample_data)
        self.assertGreater(result["total_score"], 70)
        self.assertIn("Contact Information", result["breakdown"])

    def test_job_description_matcher(self):
        cand_skills = ["Python", "SQL", "React", "Docker"]
        jd = "We are looking for a Senior Developer with expertise in Python, React, AWS, Kubernetes, and SQL."

        res = JobDescriptionMatcher.match_job_description(cand_skills, jd)
        self.assertGreater(res["match_percentage"], 0)
        self.assertIn("Python", res["matching_skills"])
        self.assertIn("AWS", res["missing_skills"])

    def test_resume_summarizer(self):
        sample_data = {
            "name": "Alex Mercer",
            "skills": ["Python", "Machine Learning", "PyTorch"],
            "education": [{"degree": "M.S. Data Science", "institution": "MIT"}],
            "experience": [{"title": "Data Scientist", "company": "AI Labs"}]
        }

        summary = ResumeSummarizer.generate_summary(sample_data)
        self.assertIn("Alex Mercer", summary)
        self.assertIn("Data Scientist", summary)


if __name__ == "__main__":
    unittest.main()
