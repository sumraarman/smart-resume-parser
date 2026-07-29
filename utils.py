"""
utils.py - Utility functions, text cleaners, skill dictionary taxonomy, logging, and export handlers.
"""

import re
import json
import logging
import unicodedata
from typing import Dict, Any, List, Set
import pandas as pd


# Configure module logger
def setup_logger(name: str = "SmartResumeParser") -> logging.Logger:
    """Configures and returns a custom logger instance.

    Args:
        name: Name of the logger module.

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


logger = setup_logger()


# Exhaustive Skill Taxonomy (Case-insensitive matching mapped to Canonical Names)
SKILL_TAXONOMY: Dict[str, List[str]] = {
    "Programming Languages": [
        "Python", "Java", "C", "C++", "C#", "JavaScript", "TypeScript", "Go", "Rust",
        "Ruby", "PHP", "Swift", "Kotlin", "R", "Scala", "Dart", "Shell", "Bash", "PowerShell"
    ],
    "Web Frameworks & Libraries": [
        "React", "Angular", "Vue.js", "Node.js", "Express.js", "Flask", "Django",
        "FastAPI", "Spring Boot", "ASP.NET", ".NET", "Next.js", "Nuxt.js", "Bootstrap", "Tailwind CSS"
    ],
    "Web Technologies": [
        "HTML", "HTML5", "CSS", "CSS3", "REST API", "GraphQL", "WebSockets", "JSON", "XML"
    ],
    "Data Science & AI/ML": [
        "Machine Learning", "Deep Learning", "NLP", "Natural Language Processing",
        "Data Science", "Computer Vision", "Pandas", "NumPy", "Matplotlib", "Seaborn",
        "Scikit-Learn", "TensorFlow", "Keras", "PyTorch", "OpenCV", "NLTK", "spaCy"
    ],
    "Data Analytics & BI": [
        "Power BI", "Tableau", "Excel", "Advanced Excel", "SQL", "DAX", "Google Data Studio", "SAS", "SPSS"
    ],
    "Databases & Storage": [
        "MongoDB", "MySQL", "PostgreSQL", "SQLite", "Oracle", "Microsoft SQL Server",
        "Redis", "Cassandra", "DynamoDB", "Firebase", "Elasticsearch"
    ],
    "Cloud & DevOps": [
        "AWS", "Azure", "Google Cloud", "GCP", "Docker", "Kubernetes", "Git", "GitHub",
        "GitLab", "Jenkins", "CI/CD", "Terraform", "Ansible", "Linux", "Unix"
    ]
}


def get_all_skills_flat() -> List[str]:
    """Flattens the skills taxonomy into a single list of unique canonical skills.

    Returns:
        List[str]: Combined list of skill keywords.
    """
    all_skills = []
    for category_skills in SKILL_TAXONOMY.values():
        all_skills.extend(category_skills)
    return list(dict.fromkeys(all_skills))


def preprocess_text(raw_text: str) -> str:
    """Cleans and normalizes raw text extracted from PDF or DOCX documents.

    Args:
        raw_text: Raw string content from document.

    Returns:
        str: Preprocessed, normalized clean text string.
    """
    if not raw_text or not raw_text.strip():
        return ""

    # Normalize Unicode characters (e.g. smart quotes, accented chars)
    normalized = unicodedata.normalize('NFKD', raw_text)

    # Convert Windows CRLF to standard LF
    text = normalized.replace('\r\n', '\n').replace('\r', '\n')

    # Remove non-printable control characters except standard whitespace
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)

    # Collapse multiple spaces on the same line into a single space
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        cleaned_line = re.sub(r'[ \t]+', ' ', line).strip()
        cleaned_lines.append(cleaned_line)

    # Remove excessive blank lines (more than 2 consecutive newlines)
    cleaned_text = '\n'.join(cleaned_lines)
    cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)

    return cleaned_text.strip()


def export_to_json(data: Dict[str, Any], indent: int = 4) -> str:
    """Serializes parsed resume data dictionary to JSON string.

    Args:
        data: Parsed resume profile dict.
        indent: Formatting indentation.

    Returns:
        str: JSON formatted string.
    """
    return json.dumps(data, indent=indent, ensure_ascii=False)


def export_to_csv(data: Dict[str, Any]) -> str:
    """Converts parsed resume data dictionary to a single-row CSV format.

    Args:
        data: Parsed resume profile dict.

    Returns:
        str: CSV string content.
    """
    flat_data = {
        "Name": data.get("name", ""),
        "Email": data.get("email", ""),
        "Phone": data.get("phone", ""),
        "Address": data.get("address", ""),
        "LinkedIn": data.get("linkedin", ""),
        "GitHub": data.get("github", ""),
        "Skills Count": len(data.get("skills", [])),
        "Skills": ", ".join(data.get("skills", [])),
        "Degrees": ", ".join([e.get("degree", "") for e in data.get("education", []) if e.get("degree")]),
        "Institutions": ", ".join([e.get("institution", "") for e in data.get("education", []) if e.get("institution")]),
        "Companies": ", ".join([exp.get("company", "") for exp in data.get("experience", []) if exp.get("company")]),
        "Job Titles": ", ".join([exp.get("title", "") for exp in data.get("experience", []) if exp.get("title")]),
        "Projects Count": len(data.get("projects", [])),
        "Certifications": ", ".join(data.get("certifications", []))
    }
    df = pd.DataFrame([flat_data])
    return df.to_csv(index=False)
