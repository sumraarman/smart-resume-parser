# 📄 Smart Resume Parser

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Web%20App-FF4B4B?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![spaCy](https://img.shields.io/badge/spaCy-NLP-09A3D5)](https://spacy.io/)
[![PyMuPDF](https://img.shields.io/badge/PyMuPDF-PDF%20Parser-green)](https://pymupdf.readthedocs.io/)
An AI-powered **Smart Resume Parser** built using **Python, Streamlit, spaCy, PyMuPDF, python-docx, and Regex**. The application extracts structured information from PDF and DOCX resumes and presents the results through a user-friendly web interface.

---

## 🚀 Features

- 📄 Upload PDF and DOCX resumes
- 📝 Extract candidate information automatically
- 👤 Name extraction
- 📧 Email extraction
- 📱 Phone number extraction
- 📍 Address extraction
- 🔗 LinkedIn profile detection
- 💻 GitHub profile detection
- 🛠 Technical skills extraction
- 🎓 Education extraction
- 💼 Work experience extraction
- 📂 Project extraction
- 📜 Certification extraction
- 📤 Export parsed data to JSON
- 📊 Export parsed data to CSV
- 🎨 Interactive Streamlit user interface
- ⚠ Error handling for unsupported or invalid files

---

## 🛠 Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| Streamlit | Web Interface |
| spaCy | Natural Language Processing |
| PyMuPDF | PDF Text Extraction |
| python-docx | DOCX Text Extraction |
| Regex | Pattern Matching |
| Pandas | Data Processing |
| JSON | Data Export |
| CSV | Data Export |

---

## 📂 Project Structure

```text
Smart_Resume_Parser/
│
├── app.py
├── parser.py
├── extractor.py
├── utils.py
├── requirements.txt
├── README.md
│
├── sample_resumes/
│   ├── Resume_Arjun_Sharma.pdf
│   ├── Resume_Priya_Patel.pdf
│   └── Resume_Rahul_Mehta.pdf
|   └── sample_data_scientist.pdf
|   └── sample_software_engineer.pdf
│
├── outputs/
│   ├── json/
│   └── csv/
│
├── assets/
│   ├── style.css
│   
│
└── tests/
```

---

## ⚙ Installation

### 1. Navigate to the Project

```bash
cd smart-resume-parser
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Download the spaCy Model

```bash
python -m spacy download en_core_web_sm
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open in your browser:

```
http://localhost:8501
```

```
assets/style.css
```

---

## 📊 Sample Output

```json
{
  "name": "Arjun Sharma",
  "email": "arjun.sharma@gmail.com",
  "phone": "+91 9876543210",
  "address": "Ahmedabad, Gujarat",
  "linkedin": "https://linkedin.com/in/arjunsharma",
  "github": "https://github.com/arjunsharma",
  "skills": [
    "Python",
    "Flask",
    "SQL",
    "Pandas",
    "Git"
  ],
  "education": [
    {
      "degree": "Master of Computer Applications",
      "institution": "Silver Oak University",
      "year": "2024"
    }
  ]
}
```

---

## 📁 Sample Resumes

The repository includes sample resumes for testing:

- Resume_Arjun_Sharma.pdf
- Resume_Priya_Patel.pdf
- Resume_Rahul_Mehta.pdf
- sample_data_scientist.pdf
- sample_software_engineer.pdf

---

## 🔮 Future Improvements

- ATS Resume Score
- Job Description Matching
- Resume Ranking
- OCR Support for Scanned PDFs
- Multi-language Resume Parsing
- Batch Resume Processing
- REST API
- User Authentication
- Database Integration

---

## 🤝 Contributing

Contributions are welcome!

1. Fork the repository
2. Create a new branch
3. Commit your changes
4. Submit a Pull Request

---

## 👨‍💻 Author

**Arman Sumra**

- GitHub: https://github.com/sumraarman
- LinkedIn: https://www.linkedin.com/in/arman-sumra-b934a8267/

---

⭐ If you found this project useful, consider giving it a **Star** on GitHub!
