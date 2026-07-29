"""
Unit tests for extractor.py module.
"""

import os
import unittest
from extractor import ResumeExtractor, UnsupportedFileFormatError, EmptyFileError, CorruptedFileError


class TestResumeExtractor(unittest.TestCase):

    def test_extract_pdf_valid(self):
        sample_pdf = "sample_resumes/sample_software_engineer.pdf"
        if os.path.exists(sample_pdf):
            text = ResumeExtractor.extract_from_pdf(sample_pdf)
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 50)
            self.assertTrue("JOHN DOE" in text or "Software Engineer" in text)

    def test_extract_docx_valid(self):
        sample_docx = "sample_resumes/sample_devops_engineer.docx"
        if os.path.exists(sample_docx):
            text = ResumeExtractor.extract_from_docx(sample_docx)
            self.assertIsInstance(text, str)
            self.assertGreater(len(text), 50)
            self.assertTrue("ROBERT JOHNSON" in text or "DevOps" in text)

    def test_unsupported_file_format(self):
        with self.assertRaises(UnsupportedFileFormatError):
            ResumeExtractor.extract_text(b"fake text content", filename="invalid_resume.txt")

    def test_empty_pdf(self):
        with self.assertRaises((EmptyFileError, CorruptedFileError)):
            ResumeExtractor.extract_from_pdf(b"")


if __name__ == "__main__":
    unittest.main()
