"""
app.py - Streamlit Interactive Frontend Application for Smart Resume Parser.
"""

import os
import json
import streamlit as st
import pandas as pd
import plotly.express as px

# Internal module imports
from extractor import ResumeExtractor, ResumeExtractorError, UnsupportedFileFormatError, CorruptedFileError, EmptyFileError
from parser import ResumeParser, get_spacy_model
from scoring import ResumeScorer, JobDescriptionMatcher, ResumeSummarizer
from database import ResumeDatabase
from utils import logger, export_to_json, export_to_csv, SKILL_TAXONOMY, get_all_skills_flat

# Page configuration
st.set_page_config(
    page_title="Smart Resume Parser - NLP Platform",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Custom CSS
def load_css(css_file="assets/style.css"):
    if os.path.exists(css_file):
        with open(css_file, "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize SQLite database
db = ResumeDatabase()

# Main Header Banner
st.markdown("""
    <div class="main-header">
        <h1>📄 Smart Resume Parser</h1>
        <p>Production-Grade NLP Engine for Structured Resume Extraction, Scoring & Job Alignment</p>
    </div>
""", unsafe_allow_html=True)

# Check spaCy model availability notification
spacy_model = get_spacy_model()
if not spacy_model:
    st.warning("⚠️ spaCy model 'en_core_web_sm' is not installed. Running in Regex & Rule-Based Fallback mode. Run `python -m spacy download en_core_web_sm` for enhanced NER.")

# Navigation Tabs
tab_parser, tab_jd, tab_batch, tab_db, tab_analytics = st.tabs([
    "📄 Single Resume Parser",
    "🎯 Job Description Matcher",
    "📂 Batch Processing",
    "🔍 Candidate Database",
    "📊 Analytics & Insights"
])


# ==========================================
# TAB 1: SINGLE RESUME PARSER
# ==========================================
with tab_parser:
    st.subheader("Upload & Parse Candidate Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF or DOCX resume file",
        type=["pdf", "docx"],
        help="Upload a PDF or Word DOCX resume to extract structured profile information."
    )

    if uploaded_file is not None:
        file_details = {"FileName": uploaded_file.name, "FileType": uploaded_file.type, "FileSize": f"{uploaded_file.size / 1024:.2f} KB"}
        st.caption(f"Uploaded: **{file_details['FileName']}** ({file_details['FileSize']})")

        with st.spinner("Extracting text and running NLP analysis..."):
            try:
                # Extract text using ResumeExtractor
                raw_text = ResumeExtractor.extract_text(uploaded_file, filename=uploaded_file.name)
                
                # Parse extracted text with ResumeParser
                parser = ResumeParser(raw_text)
                parsed_data = parser.parse()

                # Calculate Score & Summary
                score_data = ResumeScorer.calculate_score(parsed_data)
                summary_text = ResumeSummarizer.generate_summary(parsed_data)

                st.success("✅ Resume parsed successfully!")

                # --- TOP METRIC CARDS ---
                mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)
                with mcol1:
                    st.metric("Candidate Name", parsed_data.get("name") or "N/A")
                with mcol2:
                    st.metric("Email Address", parsed_data.get("email") or "N/A")
                with mcol3:
                    st.metric("Phone", parsed_data.get("phone") or "N/A")
                with mcol4:
                    st.metric("Skills Identified", len(parsed_data.get("skills", [])))
                with mcol5:
                    st.metric("Resume Score", f"{score_data['total_score']}/100")

                st.divider()

                # --- EXECUTIVE SUMMARY ---
                st.markdown("### 📝 Executive Summary")
                st.markdown(f'<div class="summary-box">{summary_text}</div>', unsafe_allow_html=True)

                # --- PERSONAL DETAILS SECTION ---
                st.markdown("### 👤 Personal & Contact Details")
                pcol1, pcol2 = st.columns(2)
                with pcol1:
                    st.write(f"**Full Name:** {parsed_data.get('name') or 'Not Detected'}")
                    st.write(f"**Email:** {parsed_data.get('email') or 'Not Detected'}")
                    st.write(f"**Phone:** {parsed_data.get('phone') or 'Not Detected'}")
                    st.write(f"**Location / Address:** {parsed_data.get('address') or 'Not Detected'}")
                with pcol2:
                    st.write(f"**LinkedIn Profile:** {parsed_data.get('linkedin') or 'Not Provided'}")
                    st.write(f"**GitHub Profile:** {parsed_data.get('github') or 'Not Provided'}")
                    st.write(f"**Portfolio / Website:** {parsed_data.get('portfolio') or 'Not Provided'}")

                st.divider()

                # --- SKILLS BADGES SECTION ---
                st.markdown("### 🛠️ Technical & Professional Skills")
                skills = parsed_data.get("skills", [])
                if skills:
                    badge_html = "".join([f'<span class="skill-badge">{skill}</span>' for skill in skills])
                    st.markdown(f"<div>{badge_html}</div>", unsafe_allow_html=True)
                else:
                    st.info("No specific technical skills were detected.")

                st.divider()

                # --- EXPERIENCE & EDUCATION TABLES ---
                col_exp, col_edu = st.columns(2)
                with col_exp:
                    st.markdown("### 💼 Work Experience")
                    exp_data = parsed_data.get("experience", [])
                    if exp_data:
                        exp_df = pd.DataFrame(exp_data)
                        st.dataframe(exp_df, use_container_width=True)
                    else:
                        st.info("No structured work experience detected.")

                with col_edu:
                    st.markdown("### 🎓 Education & Qualifications")
                    edu_data = parsed_data.get("education", [])
                    if edu_data:
                        edu_df = pd.DataFrame(edu_data)
                        st.dataframe(edu_df, use_container_width=True)
                    else:
                        st.info("No education details detected.")

                # --- PROJECTS & CERTIFICATIONS ---
                col_proj, col_cert = st.columns(2)
                with col_proj:
                    st.markdown("### 🚀 Projects")
                    proj_data = parsed_data.get("projects", [])
                    if proj_data:
                        st.dataframe(pd.DataFrame(proj_data), use_container_width=True)
                    else:
                        st.info("No projects explicitly listed.")

                with col_cert:
                    st.markdown("### 📜 Certifications")
                    cert_data = parsed_data.get("certifications", [])
                    if cert_data:
                        for cert in cert_data:
                            st.write(f"- {cert}")
                    else:
                        st.info("No certifications listed.")

                st.divider()

                # --- RESUME SCORE BREAKDOWN ---
                st.markdown("### 📊 Resume Score & Recommendations")
                scol1, scol2 = st.columns([1, 2])
                with scol1:
                    st.progress(score_data['total_score'] / 100)
                    st.markdown(f"### Score: **{score_data['total_score']} / 100**")
                    for k, v in score_data['breakdown'].items():
                        st.write(f"• **{k}:** {v}")

                with scol2:
                    st.markdown("#### Recommendations for Improvement:")
                    if score_data['recommendations']:
                        for rec in score_data['recommendations']:
                            st.warning(f"👉 {rec}")
                    else:
                        st.success("🎉 Excellent resume completeness! All key sections are well defined.")

                st.divider()

                # --- DOWNLOAD & DB SAVE BUTTONS ---
                st.markdown("### 💾 Actions & Exports")
                action_col1, action_col2, action_col3 = st.columns(3)

                json_str = export_to_json(parsed_data)
                csv_str = export_to_csv(parsed_data)

                with action_col1:
                    st.download_button(
                        label="📥 Download JSON",
                        data=json_str,
                        file_name=f"parsed_{parsed_data.get('name', 'candidate').replace(' ', '_').lower()}.json",
                        mime="application/json"
                    )

                with action_col2:
                    st.download_button(
                        label="📊 Download CSV",
                        data=csv_str,
                        file_name=f"parsed_{parsed_data.get('name', 'candidate').replace(' ', '_').lower()}.csv",
                        mime="text/csv"
                    )

                with action_col3:
                    if st.button("💾 Save Candidate to Database"):
                        saved = db.save_candidate(parsed_data, score=score_data['total_score'], raw_text=raw_text)
                        if saved:
                            st.success("Candidate record stored in SQLite database!")
                        else:
                            st.error("Failed to save candidate to database.")

            except UnsupportedFileFormatError as err:
                st.error(f"❌ File Format Error: {err}")
            except EmptyFileError as err:
                st.error(f"❌ Empty Document Error: {err}")
            except CorruptedFileError as err:
                st.error(f"❌ File Parsing Error: {err}")
            except Exception as err:
                st.error(f"❌ An unexpected error occurred: {err}")
                logger.error(f"Error processing upload: {err}", exc_info=True)


# ==========================================
# TAB 2: JOB DESCRIPTION MATCHER
# ==========================================
with tab_jd:
    st.subheader("Match Candidate Skills Against Job Description")
    st.write("Paste a job description below to analyze skill alignment and identify missing key qualifications.")

    jd_input = st.text_area("Paste Job Description Text", height=200, placeholder="Paste job requirements, skills, and qualifications here...")

    if 'parsed_data' in locals() and parsed_data:
        cand_skills = parsed_data.get("skills", [])
        st.info(f"Using parsed candidate skills from Tab 1: **{', '.join(cand_skills)}**")
    else:
        st.warning("Upload a resume in Tab 1 first, or enter manual skills below.")
        manual_skills_str = st.text_input("Enter Candidate Skills (comma-separated)", "Python, SQL, React, AWS")
        cand_skills = [s.strip() for s in manual_skills_str.split(",") if s.strip()]

    if st.button("🔍 Match Job Description"):
        if not jd_input.strip():
            st.error("Please paste job description text to proceed.")
        else:
            match_res = JobDescriptionMatcher.match_job_description(cand_skills, jd_input)

            st.markdown(f"## Compatibility Score: **{match_res['match_percentage']}%**")
            st.progress(match_res['match_percentage'] / 100)

            jcol1, jcol2 = st.columns(2)
            with jcol1:
                st.markdown("### ✅ Matching Required Skills")
                if match_res['matching_skills']:
                    badges = "".join([f'<span class="skill-badge skill-badge-matching">{s}</span>' for s in match_res['matching_skills']])
                    st.markdown(f"<div>{badges}</div>", unsafe_allow_html=True)
                else:
                    st.info("No directly matching technical skills found.")

            with jcol2:
                st.markdown("### ⚠️ Missing Required Skills")
                if match_res['missing_skills']:
                    badges = "".join([f'<span class="skill-badge skill-badge-missing">{s}</span>' for s in match_res['missing_skills']])
                    st.markdown(f"<div>{badges}</div>", unsafe_allow_html=True)
                else:
                    st.success("Candidate possesses all required skills identified in the job description!")


# ==========================================
# TAB 3: BATCH PROCESSING
# ==========================================
with tab_batch:
    st.subheader("Batch Resume Processing")
    st.write("Upload multiple resumes to parse, score, and export all candidate records simultaneously.")

    batch_files = st.file_uploader("Upload Multiple Resumes (PDF / DOCX)", type=["pdf", "docx"], accept_multiple_files=True)

    if batch_files:
        if st.button("⚡ Process All Resumes"):
            batch_results = []
            progress_bar = st.progress(0)
            status_text = st.empty()

            for idx, b_file in enumerate(batch_files):
                status_text.text(f"Processing ({idx+1}/{len(batch_files)}): {b_file.name}...")
                try:
                    r_text = ResumeExtractor.extract_text(b_file, filename=b_file.name)
                    r_parser = ResumeParser(r_text)
                    p_data = r_parser.parse()
                    s_data = ResumeScorer.calculate_score(p_data)

                    # Save to DB
                    db.save_candidate(p_data, score=s_data['total_score'], raw_text=r_text)

                    batch_results.append({
                        "Filename": b_file.name,
                        "Name": p_data.get("name") or "N/A",
                        "Email": p_data.get("email") or "N/A",
                        "Phone": p_data.get("phone") or "N/A",
                        "Skills Count": len(p_data.get("skills", [])),
                        "Top Skills": ", ".join(p_data.get("skills", [])[:5]),
                        "Score": s_data['total_score']
                    })
                except Exception as e:
                    logger.error(f"Batch processing error for {b_file.name}: {e}")
                    batch_results.append({
                        "Filename": b_file.name,
                        "Name": "ERROR",
                        "Email": str(e),
                        "Phone": "",
                        "Skills Count": 0,
                        "Top Skills": "",
                        "Score": 0
                    })

                progress_bar.progress((idx + 1) / len(batch_files))

            status_text.text("✅ Batch processing completed!")
            batch_df = pd.DataFrame(batch_results)
            st.dataframe(batch_df, use_container_width=True)

            st.download_button(
                label="📥 Download Batch Summary CSV",
                data=batch_df.to_csv(index=False),
                file_name="batch_parsed_candidates.csv",
                mime="text/csv"
            )


# ==========================================
# TAB 4: CANDIDATE DATABASE & SEARCH
# ==========================================
with tab_db:
    st.subheader("Candidate Database Management")

    scol1, scol2 = st.columns([2, 1])
    with scol1:
        search_query = st.text_input("🔍 Search by Name, Email, or Skill Keyword", "")
    with scol2:
        min_score_filter = st.slider("Filter by Minimum Score", 0, 100, 0)

    candidates = db.search_candidates(query=search_query, min_score=min_score_filter)

    if candidates:
        st.write(f"Found **{len(candidates)}** matching candidate record(s).")
        
        # Display as DataFrame
        summary_rows = []
        for c in candidates:
            summary_rows.append({
                "ID": c["id"],
                "Name": c["name"],
                "Email": c["email"],
                "Phone": c["phone"],
                "Skills": ", ".join(c.get("skills", [])),
                "Score": c["score"],
                "Date Added": c["created_at"]
            })
        st.dataframe(pd.DataFrame(summary_rows), use_container_width=True)

        if st.button("🗑️ Clear All Database Records"):
            if db.clear_all():
                st.success("Database cleared!")
                st.rerun()
    else:
        st.info("No candidates stored in database matching criteria.")


# ==========================================
# TAB 5: ANALYTICS & INSIGHTS
# ==========================================
with tab_analytics:
    st.subheader("Database Skill & Score Analytics")

    all_cand = db.get_all_candidates()

    if all_cand:
        acol1, acol2 = st.columns(2)

        # Skill Frequency Plot
        with acol1:
            st.markdown("### Top In-Demand Candidate Skills")
            skill_counts = {}
            for c in all_cand:
                for skill in c.get("skills", []):
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1

            if skill_counts:
                sdf = pd.DataFrame(list(skill_counts.items()), columns=["Skill", "Count"]).sort_values(by="Count", ascending=False).head(10)
                fig1 = px.bar(sdf, x="Count", y="Skill", orientation="h", title="Top 10 Detected Candidate Skills", color="Count", color_continuous_scale="Viridis")
                st.plotly_chart(fig1, use_container_width=True)
            else:
                st.info("No skills data available.")

        # Score Distribution Plot
        with acol2:
            st.markdown("### Candidate Score Distribution")
            scores = [c["score"] for c in all_cand]
            if scores:
                fig2 = px.histogram(scores, nbins=10, title="Resume Score Distribution", labels={'value':'Score'}, color_discrete_sequence=['#38bdf8'])
                st.plotly_chart(fig2, use_container_width=True)
            else:
                st.info("No scores available.")
    else:
        st.info("Upload and save candidate resumes to view analytics.")
