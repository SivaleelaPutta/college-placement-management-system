import os
import uuid
from flask import Flask, render_template, session, request, redirect, url_for, flash

# Import the Blueprint for the Resume Analyzer module
from resume_bp import resume_bp
from interview_bp import interview_bp

app = Flask(__name__)

# Required for session security and flash messages
app.secret_key = "placement_management_system_secret_key"

# Base configuration for image uploads
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(app.static_folder, 'images')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

# Separate Upload Folder for Resume Analyzer PDFs and DOCX files
RESUME_UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
os.makedirs(RESUME_UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = RESUME_UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024  # 10 MB limit


def allowed_file(filename):
    return (
        '.' in filename and
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )

@app.context_processor
def inject_user_data():
    return {
        "user_role": session.get("user_role", "student"),
        "profile": app.config.get("PROFILE", {})
    }

# Register the Resume Analyzer Blueprint
app.register_blueprint(resume_bp)
app.register_blueprint(interview_bp)

# ------------------------------------------------------------
# 1. RESUME CREATOR ROUTE (STUDENT SECTION)
# ------------------------------------------------------------
@app.route("/resumee")
def resumee():
    """Renders the standard Resume Creator tool."""
    return render_template("homepage.html", page="resume.html")


# ------------------------------------------------------------
# 2. STANDARD SYSTEM ROUTES
# ------------------------------------------------------------
@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login")
def login():
    role = request.args.get("role", "student")

    allowed_roles = {"student", "cdpc", "admin", "company"}

    if role not in allowed_roles:
        role = "student"

    return render_template("login.html", selected_role=role)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        roll = request.form.get("roll")
        department = request.form.get("department")
        email = request.form.get("email")
        password = request.form.get("password")

        app.config["PROFILE"] = {
            "name": name,
            "roll": roll,
            "department": department,
            "email": email,
            "phone": "Add Phone",
            "graduation": "2027",
            "cgpa": "0.0",
            "tenth": "N/A",
            "intermediate": "N/A",
            "backlogs": "0",
            "skills": "Add Skills",
            "certifications": "None",
            "linkedin": "",
            "github": ""
        }

        return redirect(url_for("home"))

    return render_template("register.html")

@app.route("/home")
def home():
    return redirect(url_for("student_dashboard"))

@app.route("/dashboard")
def dashboard():
    return redirect(url_for("student_dashboard"))

@app.route("/student/dashboard")
def student_dashboard():
    session["user_role"] = "student"

    return render_template(
        "homepage.html",
        page="dashboard.html"
    )


@app.route("/cdpc/dashboard")
def cdpc_dashboard():
    session["user_role"] = "cdpc"

    return render_template(
        "homepage.html",
        page="cdpc_dashboard.html"
    )


@app.route("/admin/dashboard")
def admin_dashboard():
    session["user_role"] = "admin"

    return render_template(
        "homepage.html",
        page="admin_dashboard.html"
    )


@app.route("/company/dashboard")
def company_dashboard():
    session["user_role"] = "company"

    return render_template(
        "homepage.html",
        page="company_dashboard.html"
    )

@app.route("/profile")
def profile():
    profile_data = app.config.get("PROFILE", {
        "name": "", "department": "", "roll": "", "email": "",
        "phone": "", "graduation": "", "cgpa": "", "tenth": "",
        "intermediate": "", "backlogs": "", "skills": "",
        "certifications": "", "linkedin": "", "github": "" 
    })

    return render_template(
        "homepage.html",
        page="profile.html",
        profile=profile_data
    )

@app.route("/companies")
def companies():
    return render_template("homepage.html", page="companies.html")

@app.route("/placement-drives")
def placement_drives():
    return render_template("homepage.html", page="placement_drives.html")

@app.route("/applications")
def applications():
    return render_template("homepage.html", page="applications.html")

@app.route("/interviewss")
def interviewss():
    return render_template("homepage.html", page="interviews.html")

@app.route("/results")
def results():
    return render_template("homepage.html", page="results.html")

@app.route("/aptitude")
def aptitude():
    years = [2025, 2024, 2023]
    return render_template('homepage.html', page='aptitude.html', years=years)

@app.route("/test/<int:year>")
def test(year):
    return f"You selected the {year} aptitude test"

@app.route('/skill')
def skill():
    return render_template("homepage.html", page="skill_assessment.html")

@app.route('/help')
def help():
    return render_template("homepage.html", page="help.html")

@app.route('/about')
def about():
    return render_template("homepage.html", page="about.html")

@app.route('/logout')
def logout():
    return render_template("homepage.html", page="logout.html")

@app.route('/confirm-logout')
def confirm_logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/update-profile", methods=["POST"])
def update_profile():
    name = request.form.get("name")
    roll = request.form.get("roll")
    email = request.form.get("email")
    phone = request.form.get("phone")
    department = request.form.get("department")
    graduation = request.form.get("graduation")

    cgpa = request.form.get("cgpa")
    tenth = request.form.get("tenth")
    intermediate = request.form.get("intermediate")
    backlogs = request.form.get("backlogs")

    skills = request.form.get("skills")
    certifications = request.form.get("certifications")

    linkedin = request.form.get("linkedin")
    github = request.form.get("github")

    profile_photo = request.files.get("profile_photo")

    if profile_photo and profile_photo.filename != "":
        if allowed_file(profile_photo.filename):
            photo_path = os.path.join(
                UPLOAD_FOLDER,
                "ME.png"
            )
            profile_photo.save(photo_path)

    app.config["PROFILE"] = {
        "name": name, "roll": roll, "email": email, "phone": phone,
        "department": department, "graduation": graduation, "cgpa": cgpa,
        "tenth": tenth, "intermediate": intermediate, "backlogs": backlogs,
        "skills": skills, "certifications": certifications,
        "linkedin": linkedin, "github": github
    }

    return redirect(url_for("profile"))


if __name__ == "__main__":
    app.run(debug=True)