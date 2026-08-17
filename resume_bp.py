import os
import uuid
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename

# Import extraction and analysis functions from your package
from resume_analyzer.extractor import extract_resume_text
from resume_analyzer.analyzer import (
    analyze_resume,
    generate_suggestions,
    match_job_description
)

# Define Blueprint
resume_bp = Blueprint('resume_bp', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ------------------------------------------------------------
# 1. RESUME ANALYZER PAGE & UPLOAD ACTION
# ------------------------------------------------------------

@resume_bp.route("/resume")
def resume_home():
    return render_template("homepage.html", page="index.html")


@resume_bp.route("/analyze", methods=["POST"])
def analyze():
    resume = request.files.get("resume")

    if not resume or resume.filename == "":
        flash("Please select a resume file.")
        return redirect(url_for("resume_bp.resume_home"))

    if not allowed_file(resume.filename):
        flash("Invalid file format. Only PDF and DOCX files are allowed.")
        return redirect(url_for("resume_bp.resume_home"))

    original_filename = secure_filename(resume.filename)
    unique_filename = f"{uuid.uuid4()}_{original_filename}"
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], unique_filename)

    try:
        resume.save(filepath)
        resume_text = extract_resume_text(filepath)
    except Exception as error:
        flash(f"Error reading resume file: {error}")
        return redirect(url_for("resume_bp.resume_home"))

    if not resume_text or len(resume_text.strip()) < 20:
        flash("No readable text found in the uploaded resume.")
        return redirect(url_for("resume_bp.resume_home"))

    try:
        analysis = analyze_resume(resume_text)
        suggestions = generate_suggestions(analysis)
    except Exception:
        suggestions = [
            "Review your overall resume structure.",
            "Include key industry-relevant technical skills.",
            "Quantify achievements in your work experience section.",
            "Tailor experience bullet points to match target job roles."
        ]

    return render_template(
        "homepage.html",
        page="result.html",
        analysis=analysis,
        suggestions=suggestions,
        filename=original_filename
    )


# ------------------------------------------------------------
# 2. JOB MATCHING PAGES & ACTION
# ------------------------------------------------------------

@resume_bp.route("/job-match", methods=["GET"])
def job_match_page():
    return render_template("homepage.html", page="job_match.html")


@resume_bp.route("/job-match", methods=["POST"])
def job_match():
    resume = request.files.get("resume")
    company_name = request.form.get("company_name", "").strip()
    job_title = request.form.get("job_title", "").strip()
    job_description = request.form.get("job_description", "").strip()

    if not resume or resume.filename == "" or not allowed_file(resume.filename):
        flash("Please upload a valid PDF or DOCX file.")
        return redirect(url_for("resume_bp.job_match_page"))

    if not job_description:
        flash("Please enter a job description.")
        return redirect(url_for("resume_bp.job_match_page"))

    original_filename = secure_filename(resume.filename)
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], f"{uuid.uuid4()}_{original_filename}")

    try:
        resume.save(filepath)
        resume_text = extract_resume_text(filepath)
        result = match_job_description(resume_text, job_description)
    except Exception as error:
        flash(f"Job matching analysis failed: {error}")
        return redirect(url_for("resume_bp.job_match_page"))

    return render_template(
        "homepage.html",
        page="job_result.html",
        result=result,
        filename=original_filename,
        company_name=company_name,
        job_title=job_title
    )