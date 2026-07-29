"""
parser.py - Comprehensive NLP & Regex Information Extraction Engine.
Extracts Personal Details, Skills, Education, Experience, Certifications, and Projects.
"""

import re
from typing import Dict, Any, List, Optional
import spacy

from utils import logger, SKILL_TAXONOMY, get_all_skills_flat


# Lazy load spaCy model with graceful fallback
_nlp_model = None

def get_spacy_model():
    """Loads spaCy model lazily with fallback handling.

    Returns:
        spacy.Language or None: Loaded spaCy NLP pipeline or None if unavailable.
    """
    global _nlp_model
    if _nlp_model is None:
        try:
            _nlp_model = spacy.load("en_core_web_sm")
            logger.info("Successfully loaded spaCy 'en_core_web_sm' model.")
        except Exception as e:
            logger.warning(
                f"Could not load spaCy 'en_core_web_sm' model ({e}). "
                "Falling back to Regex and Rule-Based extraction."
            )
            _nlp_model = False  # Sentinel indicating model load failed
    return _nlp_model if _nlp_model is not False else None


class ResumeParser:
    """Core resume parsing engine for converting raw text into structured JSON/dict."""

    # Regex patterns for contact information
    EMAIL_REGEX = re.compile(
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
        re.IGNORECASE
    )

    PHONE_REGEX = re.compile(
        r'(?:\+\d{1,3}[\s.-]?)?\(?\d{2,5}\)?[\s.-]?\d{3,4}[\s.-]?\d{3,4}',
        re.IGNORECASE
    )

    LINKEDIN_REGEX = re.compile(
        r'(?:https?://)?(?:www\.)?linkedin\.com/in/[a-zA-Z0-9_-]+/?',
        re.IGNORECASE
    )

    GITHUB_REGEX = re.compile(
        r'(?:https?://)?(?:www\.)?github\.com/[a-zA-Z0-9_-]+/?',
        re.IGNORECASE
    )

    WEBSITE_REGEX = re.compile(
        r'(?:https?://)?(?:www\.)?[a-zA-Z0-9-]+\.(?:io|me|dev|com|org|net|co)(?:/[a-zA-Z0-9_.-]*)?',
        re.IGNORECASE
    )

    DEGREE_PATTERNS = [
        r'\b(?:B\.?E\.?|B\.?Tech|Bachelor of Technology|Bachelor of Engineering)\b',
        r'\b(?:B\.?Sc|B\.?S\.?|Bachelor of Science)\b',
        r'\b(?:BCA|Bachelor of Computer Applications)\b',
        r'\b(?:M\.?E\.?|M\.?Tech|Master of Technology|Master of Engineering)\b',
        r'\b(?:M\.?Sc|M\.?S\.?|Master of Science)\b',
        r'\b(?:MCA|Master of Computer Applications)\b',
        r'\b(?:MBA|Master of Business Administration)\b',
        r'\b(?:Ph\.?D|Doctor of Philosophy)\b',
        r'\b(?:Diploma|Associate Degree|High School|Higher Secondary)\b'
    ]

    YEAR_REGEX = re.compile(r'\b(19[89]\d|20[0-2]\d)\b')
    CGPA_REGEX = re.compile(r'\b(?:CGPA|GPA|Percentage|Score)?\s*[:=]?\s*(\d{1,2}(?:\.\d{1,2})?\s*(?:/|out of)?\s*(?:10|4|100)?%?)\b', re.IGNORECASE)

    def __init__(self, raw_text: str):
        """Initializes parser with clean text input.

        Args:
            raw_text: Preprocessed text content of resume.
        """
        self.raw_text = raw_text
        self.lines = [line.strip() for line in raw_text.split('\n') if line.strip()]
        self.nlp = get_spacy_model()
        self.doc = self.nlp(raw_text[:100000]) if self.nlp else None

    def extract_name(self) -> str:
        """Extracts candidate's full name using spaCy NER and header heuristics.

        Returns:
            str: Extracted candidate name or empty string.
        """
        # Strategy 1: spaCy NER on top 5 lines
        if self.doc:
            top_text = "\n".join(self.lines[:5])
            top_doc = self.nlp(top_text)
            for ent in top_doc.ents:
                if ent.label_ == "PERSON":
                    clean_name = re.sub(r'[^a-zA-Z\s.-]', '', ent.text).strip()
                    if len(clean_name.split()) >= 2 and not any(kw in clean_name.lower() for kw in ['resume', 'curriculum', 'cv', 'page', 'email', 'phone']):
                        return clean_name.title()

        # Strategy 2: First non-empty line heuristic
        for line in self.lines[:3]:
            # Remove symbols/emails/phones
            candidate = re.sub(r'[^a-zA-Z\s]', '', line).strip()
            words = candidate.split()
            if 2 <= len(words) <= 4:
                lower_words = [w.lower() for w in words]
                if not any(w in lower_words for w in ['resume', 'curriculum', 'vitae', 'cv', 'profile', 'developer', 'engineer', 'contact', 'summary']):
                    return candidate.title()

        return ""

    def extract_email(self) -> str:
        """Extracts primary email address.

        Returns:
            str: Extracted email or empty string.
        """
        matches = self.EMAIL_REGEX.findall(self.raw_text)
        return matches[0] if matches else ""

    def extract_phone(self) -> str:
        """Extracts primary phone number.

        Returns:
            str: Extracted phone number or empty string.
        """
        matches = self.PHONE_REGEX.findall(self.raw_text)
        for match in matches:
            cleaned = re.sub(r'\s+', ' ', match).strip()
            # Must contain at least 7 digits to avoid date false positives
            digits = re.sub(r'\D', '', cleaned)
            if 7 <= len(digits) <= 15:
                return cleaned
        return ""

    def extract_address(self) -> str:
        """Extracts physical address or location.

        Returns:
            str: Extracted address or location.
        """
        if self.doc:
            locations = []
            for ent in self.doc.ents:
                if ent.label_ in ["GPE", "LOC"]:
                    locations.append(ent.text)
            if locations:
                # Return unique location entities found early in text
                unique_locs = list(dict.fromkeys(locations[:3]))
                return ", ".join(unique_locs)

        # Heuristic fallback using common address keywords
        for line in self.lines[:15]:
            if any(kw in line.lower() for kw in ['street', 'avenue', 'road', 'city', 'state', 'pincode', 'zipcode', 'india', 'usa', 'uk']):
                if not self.EMAIL_REGEX.search(line):
                    return line
        return ""

    def extract_social_links(self) -> Dict[str, str]:
        """Extracts LinkedIn, GitHub, and Portfolio URLs.

        Returns:
            Dict[str, str]: Social profile URLs.
        """
        linkedin = self.LINKEDIN_REGEX.search(self.raw_text)
        github = self.GITHUB_REGEX.search(self.raw_text)

        # Portfolio search excluding linkedin/github
        website = None
        for match in self.WEBSITE_REGEX.finditer(self.raw_text):
            url = match.group(0)
            if 'linkedin.com' not in url.lower() and 'github.com' not in url.lower():
                website = url
                break

        return {
            "linkedin": linkedin.group(0) if linkedin else "",
            "github": github.group(0) if github else "",
            "portfolio": website if website else ""
        }

    def extract_skills(self) -> List[str]:
        """Extracts technical skills without duplicates based on taxonomy mapping.

        Returns:
            List[str]: List of recognized skill names.
        """
        detected_skills: Set[str] = set()

        all_flat_skills = get_all_skills_flat()
        text_lower = f" {self.raw_text.lower()} "

        # Boundary aware regex matching for skills
        for skill in all_flat_skills:
            # Escape skill name for regex
            escaped_skill = re.escape(skill.lower())
            
            # Special regex handling for skills with C/C++/C#/.NET
            if skill in ["C", "C++", "C#", ".NET"]:
                pattern = r'(?<=[\s,;:()/])' + escaped_skill + r'(?=[\s,;:()/])'
            else:
                pattern = r'\b' + escaped_skill + r'\b'

            if re.search(pattern, text_lower, re.IGNORECASE):
                detected_skills.add(skill)

        return sorted(list(detected_skills))

    def extract_education(self) -> List[Dict[str, str]]:
        """Extracts education details including Degree, Institution, Year, and CGPA.

        Returns:
            List[Dict[str, str]]: List of education objects.
        """
        education_list = []

        # Find section lines corresponding to Education
        edu_section_lines = self._extract_section_text(['education', 'academic background', 'qualification', 'academic details'])

        target_lines = edu_section_lines if edu_section_lines else self.lines

        for idx, line in enumerate(target_lines):
            for degree_pat in self.DEGREE_PATTERNS:
                degree_match = re.search(degree_pat, line, re.IGNORECASE)
                if degree_match:
                    degree_str = degree_match.group(0)

                    # Context window around degree line to find university & year
                    context_window = " ".join(target_lines[max(0, idx - 1): min(len(target_lines), idx + 3)])

                    # Find Year
                    years = self.YEAR_REGEX.findall(context_window)
                    year_str = years[-1] if years else ""

                    # Find CGPA/Percentage
                    cgpa_match = self.CGPA_REGEX.search(context_window)
                    cgpa_str = cgpa_match.group(0) if cgpa_match else ""

                    # Find Institution name heuristic (e.g. University, Institute, College)
                    inst_match = re.search(r'([A-Z][a-zA-Z\s&]+(?:University|Institute|College|School|Academy)[a-zA-Z\s&]*)', context_window)
                    inst_str = inst_match.group(0).strip() if inst_match else ""

                    edu_entry = {
                        "degree": degree_str,
                        "institution": inst_str,
                        "branch": "",
                        "year": year_str,
                        "score": cgpa_str
                    }

                    # Avoid exact duplicates
                    if not any(e["degree"].lower() == degree_str.lower() for e in education_list):
                        education_list.append(edu_entry)

        return education_list

    def extract_experience(self) -> List[Dict[str, str]]:
        """Extracts work experience, company names, job titles, duration, and responsibilities.

        Returns:
            List[Dict[str, str]]: List of experience objects.
        """
        experience_list = []
        exp_lines = self._extract_section_text(['experience', 'work history', 'employment', 'professional background'])

        if not exp_lines:
            return experience_list

        current_entry = None
        date_pattern = re.compile(
            r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*(?:19|20)\d{2}\s*[-–—\s\t]+(?:Present|Current|Till Date|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|January|February|March|April|May|June|July|August|September|October|November|December)?\s*(?:19|20)\d{2})\b',
            re.IGNORECASE
        )

        for line in exp_lines:
            date_match = date_pattern.search(line)
            if date_match or any(title_kw in line.lower() for title_kw in ['developer', 'engineer', 'analyst', 'manager', 'lead', 'intern', 'consultant', 'architect']):
                if current_entry:
                    experience_list.append(current_entry)

                duration = date_match.group(0) if date_match else ""
                title_line = date_pattern.sub('', line).strip(' |-–—')

                current_entry = {
                    "company": "",
                    "title": title_line if title_line else "Software Professional",
                    "duration": duration,
                    "responsibilities": []
                }
                
                # Check for Organization entity via spaCy
                if self.nlp:
                    line_doc = self.nlp(line)
                    for ent in line_doc.ents:
                        if ent.label_ == "ORG":
                            current_entry["company"] = ent.text
                            break
            elif current_entry:
                if line.startswith(('•', '-', '*', '1.', '2.', '3.')) or len(line) > 20:
                    clean_resp = line.lstrip('•-*123456789. ').strip()
                    if clean_resp:
                        current_entry["responsibilities"].append(clean_resp)

        if current_entry:
            experience_list.append(current_entry)

        return experience_list

    def extract_certifications(self) -> List[str]:
        """Extracts certifications and licenses.

        Returns:
            List[str]: List of certification names.
        """
        certs = []
        cert_lines = self._extract_section_text(['certification', 'certifications', 'licenses', 'courses'])

        for line in cert_lines:
            clean = line.lstrip('•-*123456789. ').strip()
            if clean and len(clean) > 3 and not any(header in clean.lower() for header in ['certification', 'courses']):
                certs.append(clean)

        return certs[:10]  # Cap at top 10

    def extract_projects(self) -> List[Dict[str, str]]:
        """Extracts technical projects, technologies used, and descriptions.

        Returns:
            List[Dict[str, str]]: List of project objects.
        """
        projects = []
        project_lines = self._extract_section_text(['project', 'projects', 'academic projects', 'key projects'])

        current_proj = None
        for line in project_lines:
            if line.startswith(('•', '-', '*')) or (current_proj and not current_proj["description"]):
                if current_proj:
                    current_proj["description"].append(line.lstrip('•-* ').strip())
            else:
                if current_proj and current_proj["title"]:
                    current_proj["description"] = " ".join(current_proj["description"])
                    projects.append(current_proj)

                current_proj = {
                    "title": line.strip(' :|-'),
                    "technologies": "",
                    "description": []
                }

        if current_proj and current_proj["title"]:
            current_proj["description"] = " ".join(current_proj["description"]) if isinstance(current_proj["description"], list) else current_proj["description"]
            projects.append(current_proj)

        return projects

    def _extract_section_text(self, section_headers: List[str]) -> List[str]:
        """Helper to isolate text lines belonging to specific section headers.

        Args:
            section_headers: List of target header keywords.

        Returns:
            List[str]: Lines belonging to that section.
        """
        section_lines = []
        in_section = False

        known_headers = [
            'education', 'experience', 'skills', 'projects', 'certifications',
            'summary', 'profile', 'work history', 'academic background', 'contact'
        ]

        for line in self.lines:
            line_lower = line.lower().strip(': ')

            # Check if line is target section header
            if any(hdr in line_lower for hdr in section_headers) and len(line.split()) <= 4:
                in_section = True
                continue

            # Check if line is another section header (stop capturing)
            if in_section:
                if any(hdr in line_lower for hdr in known_headers) and not any(hdr in line_lower for hdr in section_headers) and len(line.split()) <= 4:
                    break
                section_lines.append(line)

        return section_lines

    def parse(self) -> Dict[str, Any]:
        """Parses raw text and returns structured dictionary format.

        Returns:
            Dict[str, Any]: Standardized JSON schema data structure.
        """
        social = self.extract_social_links()

        return {
            "name": self.extract_name(),
            "email": self.extract_email(),
            "phone": self.extract_phone(),
            "address": self.extract_address(),
            "linkedin": social["linkedin"],
            "github": social["github"],
            "portfolio": social["portfolio"],
            "skills": self.extract_skills(),
            "education": self.extract_education(),
            "experience": self.extract_experience(),
            "projects": self.extract_projects(),
            "certifications": self.extract_certifications()
        }
