"""
Unit tests for parser.py module.
"""

import unittest
from parser import ResumeParser

SAMPLE_TEXT = """
SARAH CONNOR
Email: sarah.connor@cyberdyne.com
Phone: +1 (555) 019-2834
Location: Los Angeles, CA
LinkedIn: https://linkedin.com/in/sarah-connor
GitHub: https://github.com/sarah-connor

TECHNICAL SKILLS
Programming: Python, Java, C++, SQL, JavaScript
Frameworks: React, Django, Flask, Node.js
Databases: PostgreSQL, MongoDB, Redis
Cloud & DevOps: AWS, Docker, Kubernetes, Git

WORK EXPERIENCE
Senior AI Engineer | Cyberdyne Systems
Jan 2021 - Present
- Built machine learning and computer vision neural networks in Python and PyTorch.

EDUCATION
Bachelor of Science in Computer Science
Stanford University (2016 - 2020)
GPA: 3.9 / 4.0
"""


class TestResumeParser(unittest.TestCase):

    def test_parser_personal_details(self):
        parser = ResumeParser(SAMPLE_TEXT)
        data = parser.parse()

        self.assertTrue("Sarah" in data["name"] or data["name"] == "Sarah Connor")
        self.assertEqual(data["email"], "sarah.connor@cyberdyne.com")
        self.assertIn("555", data["phone"])
        self.assertEqual(data["linkedin"], "https://linkedin.com/in/sarah-connor")
        self.assertEqual(data["github"], "https://github.com/sarah-connor")

    def test_parser_skills_extraction(self):
        parser = ResumeParser(SAMPLE_TEXT)
        data = parser.parse()

        skills = data["skills"]
        self.assertIn("Python", skills)
        self.assertIn("Java", skills)
        self.assertIn("React", skills)
        self.assertIn("AWS", skills)
        self.assertIn("Docker", skills)

    def test_parser_education(self):
        parser = ResumeParser(SAMPLE_TEXT)
        data = parser.parse()

        edu = data["education"]
        self.assertGreaterEqual(len(edu), 1)


if __name__ == "__main__":
    unittest.main()
