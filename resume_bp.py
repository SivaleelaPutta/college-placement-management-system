import os
import uuid

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    current_app,
    session
)

from werkzeug.utils import secure_filename

from resume_analyzer.extractor import extract_resume_text

from resume_analyzer.analyzer import (
    analyze_resume,
    generate_suggestions,
    match_job_description
)


# ============================================================
# BLUEPRINT
# ============================================================

resume_bp = Blueprint(
    "resume_bp",
    __name__,
    url_prefix="/resume-analyzer"
)


# ============================================================
# CONFIGURATION
# ============================================================

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx"
}

MAX_RESUME_SIZE = 10 * 1024 * 1024  # 10 MB


# ============================================================
# CHECK FILE TYPE
# ============================================================

def allowed_file(filename):
    """
    Check whether the uploaded file has
    an allowed extension.
    """

    return (
        bool(filename)
        and "." in filename
        and filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )


# ============================================================
# LOGIN CHECK
# ============================================================

def resume_login_required():
    """
    Check whether the user is logged in.
    """

    return session.get("logged_in") is True


# ============================================================
# DELETE TEMPORARY FILE
# ============================================================

def delete_uploaded_file(filepath):
    """
    Safely delete a temporary uploaded file.
    """

    if not filepath:
        return

    try:

        if os.path.isfile(filepath):

            os.remove(filepath)

            print(
                "TEMP FILE DELETED:",
                filepath
            )

    except OSError as error:

        print(
            "FILE DELETE ERROR:",
            error
        )


# ============================================================
# SAVE UPLOADED RESUME
# ============================================================

def save_uploaded_file(uploaded_file):
    """
    Validate and save an uploaded resume.

    Returns:
        filepath, original_filename

    Raises:
        ValueError if validation fails.
    """

    # --------------------------------------------------------
    # Check file
    # --------------------------------------------------------

    if not uploaded_file:

        raise ValueError(
            "Please select a resume file."
        )

    if not uploaded_file.filename:

        raise ValueError(
            "Please select a resume file."
        )

    # --------------------------------------------------------
    # Secure filename
    # --------------------------------------------------------

    original_filename = secure_filename(
        uploaded_file.filename
    )

    if not original_filename:

        raise ValueError(
            "Invalid filename."
        )

    # --------------------------------------------------------
    # Check extension
    # --------------------------------------------------------

    if not allowed_file(original_filename):

        raise ValueError(
            "Invalid file format. "
            "Only PDF and DOCX files are allowed."
        )

    # --------------------------------------------------------
    # Check request size
    # --------------------------------------------------------

    content_length = request.content_length

    if (
        content_length is not None
        and content_length > MAX_RESUME_SIZE
    ):

        raise ValueError(
            "Resume file is too large. "
            "Maximum allowed size is 10 MB."
        )

    # --------------------------------------------------------
    # Get upload folder
    # --------------------------------------------------------

    upload_folder = current_app.config.get(
        "UPLOAD_FOLDER"
    )

    if not upload_folder:

        raise ValueError(
            "Upload folder is not configured."
        )

    os.makedirs(
        upload_folder,
        exist_ok=True
    )

    # --------------------------------------------------------
    # Create unique filename
    # --------------------------------------------------------

    unique_filename = (
        f"{uuid.uuid4().hex}_{original_filename}"
    )

    filepath = os.path.join(
        upload_folder,
        unique_filename
    )

    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    uploaded_file.save(
        filepath
    )

    # --------------------------------------------------------
    # Check actual file size
    # --------------------------------------------------------

    try:

        file_size = os.path.getsize(
            filepath
        )

    except OSError:

        delete_uploaded_file(
            filepath
        )

        raise ValueError(
            "Unable to verify uploaded file."
        )

    if file_size > MAX_RESUME_SIZE:

        delete_uploaded_file(
            filepath
        )

        raise ValueError(
            "Resume file is too large. "
            "Maximum allowed size is 10 MB."
        )

    return (
        filepath,
        original_filename
    )


# ============================================================
# 1. RESUME ANALYZER HOME PAGE
# ============================================================

@resume_bp.route(
    "/resume",
    methods=["GET"]
)
def resume_home():

    if not resume_login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="index.html"
    )


# ============================================================
# 2. RESUME ANALYSIS
# ============================================================

@resume_bp.route(
    "/analyze",
    methods=["POST"]
)
def analyze():

    if not resume_login_required():

        return redirect(
            url_for("login")
        )

    filepath = None
    original_filename = None

    try:

        # ----------------------------------------------------
        # Get uploaded resume
        # ----------------------------------------------------

        resume = request.files.get(
            "resume"
        )

        # ----------------------------------------------------
        # Save and validate resume
        # ----------------------------------------------------

        filepath, original_filename = save_uploaded_file(
            resume
        )

        # ----------------------------------------------------
        # Extract text
        # ----------------------------------------------------

        resume_text = extract_resume_text(
            filepath
        )

        if (
            not resume_text
            or len(resume_text.strip()) < 20
        ):

            raise ValueError(
                "No readable text found in the uploaded resume."
            )

        # ----------------------------------------------------
        # Analyze resume
        # ----------------------------------------------------

        try:

            analysis = analyze_resume(
                resume_text
            )

            suggestions = generate_suggestions(
                analysis
            )

        except Exception as error:

            print(
                "RESUME ANALYSIS ERROR:",
                error
            )

            # Keep the application usable
            # if the analyzer fails.

            analysis = {}

            suggestions = [
                "Review your overall resume structure.",
                "Include key industry-relevant technical skills.",
                "Quantify achievements in your work experience section.",
                "Tailor your resume to the target job role.",
                "Add relevant projects and certifications."
            ]

        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        return render_template(
            "homepage.html",
            page="result.html",
            analysis=analysis,
            suggestions=suggestions,
            filename=original_filename
        )

    except ValueError as error:

        print(
            "RESUME VALIDATION ERROR:",
            error
        )

        flash(
            str(error),
            "error"
        )

        return redirect(
            url_for(
                "resume_bp.resume_home"
            )
        )

    except Exception as error:

        print(
            "RESUME PROCESSING ERROR:",
            error
        )

        flash(
            "Unable to process the uploaded resume. "
            "Please try another PDF or DOCX file.",
            "error"
        )

        return redirect(
            url_for(
                "resume_bp.resume_home"
            )
        )

    finally:

        # ----------------------------------------------------
        # Always delete temporary file
        # ----------------------------------------------------

        delete_uploaded_file(
            filepath
        )


# ============================================================
# 3. JOB MATCHING PAGE
# ============================================================

@resume_bp.route(
    "/job-match",
    methods=["GET"]
)
def job_match_page():

    if not resume_login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="job_match.html"
    )


# ============================================================
# 4. JOB MATCHING ANALYSIS
# ============================================================

@resume_bp.route(
    "/job-match",
    methods=["POST"]
)
def job_match():

    if not resume_login_required():

        return redirect(
            url_for("login")
        )

    filepath = None
    original_filename = None

    try:

        # ----------------------------------------------------
        # Get uploaded resume
        # ----------------------------------------------------

        resume = request.files.get(
            "resume"
        )

        # ----------------------------------------------------
        # Get job details
        # ----------------------------------------------------

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        job_title = request.form.get(
            "job_title",
            ""
        ).strip()

        job_description = request.form.get(
            "job_description",
            ""
        ).strip()

        # ----------------------------------------------------
        # Validate job description
        # ----------------------------------------------------

        if not job_description:

            raise ValueError(
                "Please enter a job description."
            )

        # ----------------------------------------------------
        # Save resume
        # ----------------------------------------------------

        filepath, original_filename = save_uploaded_file(
            resume
        )

        # ----------------------------------------------------
        # Extract resume text
        # ----------------------------------------------------

        resume_text = extract_resume_text(
            filepath
        )

        if (
            not resume_text
            or len(resume_text.strip()) < 20
        ):

            raise ValueError(
                "No readable text found in the uploaded resume."
            )

        # ----------------------------------------------------
        # Match resume with job description
        # ----------------------------------------------------

        result = match_job_description(
            resume_text,
            job_description
        )

        # ----------------------------------------------------
        # Display result
        # ----------------------------------------------------

        return render_template(
            "homepage.html",
            page="job_result.html",
            result=result,
            filename=original_filename,
            company_name=company_name,
            job_title=job_title
        )

    except ValueError as error:

        print(
            "JOB MATCH VALIDATION ERROR:",
            error
        )

        flash(
            str(error),
            "error"
        )

        return redirect(
            url_for(
                "resume_bp.job_match_page"
            )
        )

    except Exception as error:

        print(
            "JOB MATCH ERROR:",
            error
        )

        flash(
            "Job matching analysis failed. "
            "Please check the uploaded resume and try again.",
            "error"
        )

        return redirect(
            url_for(
                "resume_bp.job_match_page"
            )
        )

    finally:

        # ----------------------------------------------------
        # Always delete temporary file
        # ----------------------------------------------------

        delete_uploaded_file(
            filepath
        )