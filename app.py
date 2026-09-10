import os

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    session,
    flash
)

import mysql.connector
from mysql.connector import Error

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

# ============================================================
# BLUEPRINT IMPORTS
# ============================================================

from resume_bp import resume_bp
from interview_bp import interview_bp


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)

app.secret_key = "CPMS_RGUKT_SECRET_KEY_2026"


# ============================================================
# MYSQL DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": "localhost",
    "user": "sivaleela",
    "password": "Sivaleela@19",
    "database": "cpms_db"
}


# ============================================================
# FOLDERS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

IMAGE_FOLDER = os.path.join(
    BASE_DIR,
    "static",
    "images"
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

os.makedirs(
    IMAGE_FOLDER,
    exist_ok=True
)

os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

app.config["IMAGE_FOLDER"] = IMAGE_FOLDER
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

# Maximum upload size = 10 MB
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_db_connection():

    try:

        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"]
        )

        return connection

    except Error as e:

        print(
            "MYSQL CONNECTION ERROR:",
            e
        )

        return None


# ============================================================
# REGISTER BLUEPRINTS
# ============================================================

app.register_blueprint(resume_bp)
app.register_blueprint(interview_bp)


# ============================================================
# FILE TOO LARGE ERROR
# ============================================================

@app.errorhandler(413)
def request_entity_too_large(error):

    flash(
        "Uploaded file is too large. Maximum allowed size is 10 MB.",
        "error"
    )

    return redirect(
        url_for("resume_bp.resume_home")
    )


# ============================================================
# LOGIN REQUIRED
# ============================================================

def login_required():

    return session.get("logged_in") is True


# ============================================================
# LANDING PAGE
# ============================================================

@app.route("/")
def landing():

    return render_template(
        "landing.html"
    )


# ============================================================
# LOGIN
# ============================================================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        ).strip().lower()

        if not email or not password or not role:

            flash(
                "Please enter email, password and account type.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        valid_roles = [
            "student",
            "admin",
            "cdpc",
            "company"
        ]

        if role not in valid_roles:

            flash(
                "Invalid account type.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        connection = get_db_connection()

        if connection is None:

            flash(
                "Database connection failed. Check MySQL.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        cursor = connection.cursor(
            dictionary=True
        )

        try:

            cursor.execute(
                """
                SELECT
                    user_id,
                    full_name,
                    email,
                    password,
                    role
                FROM users
                WHERE email = %s
                AND role = %s
                """,
                (
                    email,
                    role
                )
            )

            user = cursor.fetchone()

            if user is None:

                flash(
                    "Account not found for the selected role.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            if not check_password_hash(
                user["password"],
                password
            ):

                flash(
                    "Incorrect password.",
                    "error"
                )

                return redirect(
                    url_for("login")
                )

            session.clear()

            session["logged_in"] = True
            session["user_id"] = user["user_id"]
            session["full_name"] = user["full_name"]
            session["email"] = user["email"]
            session["role"] = user["role"]

            return redirect(
                url_for("dashboard")
            )

        except Error as e:

            print(
                "LOGIN ERROR:",
                e
            )

            flash(
                "Login failed.",
                "error"
            )

            return redirect(
                url_for("login")
            )

        finally:

            cursor.close()
            connection.close()

    return render_template(
        "login.html"
    )


# ============================================================
# REGISTRATION
# ============================================================

@app.route(
    "/register",
    methods=["GET", "POST"]
)
def register():

    if request.method == "POST":

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        role = request.form.get(
            "role",
            ""
        ).strip().lower()

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not full_name:

            flash(
                "Please enter your full name.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if not email:

            flash(
                "Please enter your email.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if not password:

            flash(
                "Please enter a password.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        if len(password) < 6:

            flash(
                "Password must contain at least 6 characters.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        valid_roles = [
            "student",
            "admin",
            "cdpc",
            "company"
        ]

        if role not in valid_roles:

            flash(
                "Please select a valid account type.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        # ----------------------------------------------------
        # STUDENT DETAILS
        # ----------------------------------------------------

        roll_number = request.form.get(
            "roll_number",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        dob = request.form.get(
            "dob",
            ""
        ).strip()

        gender = request.form.get(
            "gender",
            ""
        ).strip()

        address = request.form.get(
            "address",
            ""
        ).strip()

        # ----------------------------------------------------
        # COMPANY DETAILS
        # ----------------------------------------------------

        company_name = request.form.get(
            "company_name",
            ""
        ).strip()

        industry = request.form.get(
            "industry",
            ""
        ).strip()

        location = request.form.get(
            "location",
            ""
        ).strip()

        website = request.form.get(
            "website",
            ""
        ).strip()

        description = request.form.get(
            "description",
            ""
        ).strip()

        password_hash = generate_password_hash(
            password
        )

        connection = get_db_connection()

        if connection is None:

            flash(
                "Database connection failed. Check MySQL.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        cursor = connection.cursor()

        try:

            # ------------------------------------------------
            # CHECK EXISTING USER
            # ------------------------------------------------

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "This email is already registered.",
                    "error"
                )

                return redirect(
                    url_for("register")
                )

            # ------------------------------------------------
            # COMPANY VALIDATION
            # ------------------------------------------------

            if role == "company" and not company_name:

                flash(
                    "Company name is required.",
                    "error"
                )

                return redirect(
                    url_for("register")
                )

            # ------------------------------------------------
            # INSERT USER
            # ------------------------------------------------

            cursor.execute(
                """
                INSERT INTO users
                (
                    full_name,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    full_name,
                    email,
                    password_hash,
                    role
                )
            )

            user_id = cursor.lastrowid

            # ------------------------------------------------
            # INSERT STUDENT PROFILE
            # ------------------------------------------------

            if role == "student":

                year_value = (
                    int(year)
                    if year.isdigit()
                    else None
                )

                cursor.execute(
                    """
                    INSERT INTO students
                    (
                        user_id,
                        roll_number,
                        branch,
                        year,
                        phone,
                        dob,
                        gender,
                        address
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        user_id,
                        roll_number or None,
                        branch or None,
                        year_value,
                        phone or None,
                        dob or None,
                        gender or None,
                        address or None
                    )
                )

            # ------------------------------------------------
            # INSERT COMPANY PROFILE
            # ------------------------------------------------

            elif role == "company":

                cursor.execute(
                    """
                    INSERT INTO companies
                    (
                        user_id,
                        company_name,
                        industry,
                        location,
                        website,
                        description
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        %s,
                        %s,
                        %s
                    )
                    """,
                    (
                        user_id,
                        company_name,
                        industry or None,
                        location or None,
                        website or None,
                        description or None
                    )
                )

            connection.commit()

            flash(
                "Registration successful. Please login.",
                "success"
            )

            return redirect(
                url_for("login")
            )

        except Error as e:

            connection.rollback()

            print(
                "REGISTRATION ERROR:",
                e
            )

            flash(
                "Registration failed. Please try again.",
                "error"
            )

            return redirect(
                url_for("register")
            )

        finally:

            cursor.close()
            connection.close()

    return render_template(
        "register.html"
    )


# ============================================================
# DASHBOARD STATISTICS
# ============================================================

def get_dashboard_stats(
    role,
    user_id
):

    stats = {
        "companies": 0,
        "applications": 0,
        "interviews": 0,
        "offers": 0,
        "students": 0,
        "drives": 0,
        "shortlisted": 0,
        "results": 0
    }

    connection = get_db_connection()

    if connection is None:
        return stats

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # ====================================================
        # STUDENT
        # ====================================================

        if role == "student":

            cursor.execute(
                """
                SELECT student_id
                FROM students
                WHERE user_id = %s
                """,
                (user_id,)
            )

            student = cursor.fetchone()

            if student:

                student_id = student["student_id"]

                # Open placement drives

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM placement_drives
                    WHERE status = 'Open'
                    """
                )

                stats["companies"] = (
                    cursor.fetchone()["total"]
                )

                # Applications

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM applications
                    WHERE student_id = %s
                    """,
                    (student_id,)
                )

                stats["applications"] = (
                    cursor.fetchone()["total"]
                )

                # Interviews

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM interviews i
                    INNER JOIN applications a
                        ON i.application_id =
                           a.application_id
                    WHERE a.student_id = %s
                    """,
                    (student_id,)
                )

                stats["interviews"] = (
                    cursor.fetchone()["total"]
                )

                # Offers

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM results r
                    INNER JOIN applications a
                        ON r.application_id =
                           a.application_id
                    WHERE a.student_id = %s
                    AND r.result_status = 'Selected'
                    """,
                    (student_id,)
                )

                stats["offers"] = (
                    cursor.fetchone()["total"]
                )

        # ====================================================
        # ADMIN / CDPC
        # ====================================================

        elif role in [
            "admin",
            "cdpc"
        ]:

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM students
                """
            )

            stats["students"] = (
                cursor.fetchone()["total"]
            )

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM companies
                """
            )

            stats["companies"] = (
                cursor.fetchone()["total"]
            )

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM placement_drives
                """
            )

            stats["drives"] = (
                cursor.fetchone()["total"]
            )

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM applications
                """
            )

            stats["applications"] = (
                cursor.fetchone()["total"]
            )

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM interviews
                """
            )

            stats["interviews"] = (
                cursor.fetchone()["total"]
            )

            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM results
                WHERE result_status = 'Selected'
                """
            )

            stats["offers"] = (
                cursor.fetchone()["total"]
            )

        # ====================================================
        # COMPANY
        # ====================================================

        elif role == "company":

            cursor.execute(
                """
                SELECT company_id
                FROM companies
                WHERE user_id = %s
                """,
                (user_id,)
            )

            company = cursor.fetchone()

            if company:

                company_id = company["company_id"]

                # Drives

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM placement_drives
                    WHERE company_id = %s
                    """,
                    (company_id,)
                )

                stats["drives"] = (
                    cursor.fetchone()["total"]
                )

                # Applications

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM applications a
                    INNER JOIN placement_drives d
                        ON a.drive_id = d.drive_id
                    WHERE d.company_id = %s
                    """,
                    (company_id,)
                )

                stats["applications"] = (
                    cursor.fetchone()["total"]
                )

                # Shortlisted

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM applications a
                    INNER JOIN placement_drives d
                        ON a.drive_id = d.drive_id
                    WHERE d.company_id = %s
                    AND a.status = 'Shortlisted'
                    """,
                    (company_id,)
                )

                stats["shortlisted"] = (
                    cursor.fetchone()["total"]
                )

                # Interviews

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM interviews i
                    INNER JOIN applications a
                        ON i.application_id =
                           a.application_id
                    INNER JOIN placement_drives d
                        ON a.drive_id = d.drive_id
                    WHERE d.company_id = %s
                    """,
                    (company_id,)
                )

                stats["interviews"] = (
                    cursor.fetchone()["total"]
                )

                # Offers

                cursor.execute(
                    """
                    SELECT COUNT(*) AS total
                    FROM results r
                    INNER JOIN applications a
                        ON r.application_id =
                           a.application_id
                    INNER JOIN placement_drives d
                        ON a.drive_id = d.drive_id
                    WHERE d.company_id = %s
                    AND r.result_status = 'Selected'
                    """,
                    (company_id,)
                )

                stats["offers"] = (
                    cursor.fetchone()["total"]
                )

        return stats

    except Error as e:

        print(
            "DASHBOARD STATS ERROR:",
            e
        )

        return stats

    finally:

        cursor.close()
        connection.close()


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )

    role = session.get("role")
    user_id = session.get("user_id")

    valid_roles = [
        "student",
        "admin",
        "cdpc",
        "company"
    ]

    if role not in valid_roles:

        session.clear()

        return redirect(
            url_for("landing")
        )

    stats = get_dashboard_stats(
        role,
        user_id
    )

    return render_template(
        "homepage.html",
        page="dashboard.html",
        role=role,
        stats=stats,
        user_name=session.get("full_name"),
        email=session.get("email")
    )


# ============================================================
# ROLE DASHBOARD
# ============================================================

@app.route("/role-dashboard")
def role_dashboard():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("dashboard")
    )


# ============================================================
# PROFILE
# ============================================================

@app.route("/profile")
def profile():

    if not login_required():

        return redirect(
            url_for("login")
        )

    user_id = session.get("user_id")
    role = session.get("role")

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        profile_data = None

        # ----------------------------------------------------
        # STUDENT PROFILE
        # ----------------------------------------------------

        if role == "student":

            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.full_name,
                    u.email,
                    u.role,
                    u.created_at,
                    s.student_id,
                    s.roll_number,
                    s.branch,
                    s.year,
                    s.phone,
                    s.dob,
                    s.gender,
                    s.address
                FROM users u
                INNER JOIN students s
                    ON u.user_id = s.user_id
                WHERE u.user_id = %s
                """,
                (user_id,)
            )

            profile_data = cursor.fetchone()

        # ----------------------------------------------------
        # ADMIN / CDPC PROFILE
        # ----------------------------------------------------

        elif role in [
            "admin",
            "cdpc"
        ]:

            cursor.execute(
                """
                SELECT
                    user_id,
                    full_name,
                    email,
                    role,
                    created_at
                FROM users
                WHERE user_id = %s
                """,
                (user_id,)
            )

            profile_data = cursor.fetchone()

        # ----------------------------------------------------
        # COMPANY PROFILE
        # ----------------------------------------------------

        elif role == "company":

            cursor.execute(
                """
                SELECT
                    u.user_id,
                    u.full_name,
                    u.email,
                    u.role,
                    u.created_at,
                    c.company_id,
                    c.company_name,
                    c.industry,
                    c.location,
                    c.website,
                    c.description
                FROM users u
                INNER JOIN companies c
                    ON u.user_id = c.user_id
                WHERE u.user_id = %s
                """,
                (user_id,)
            )

            profile_data = cursor.fetchone()

        if profile_data is None:

            flash(
                "Profile information not found.",
                "error"
            )

            return redirect(
                url_for("dashboard")
            )

        return render_template(
            "homepage.html",
            page="profile.html",
            profile=profile_data
        )

    except Error as e:

        print(
            "PROFILE ERROR:",
            e
        )

        flash(
            "Unable to load profile.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# UPDATE PROFILE
# ============================================================

@app.route(
    "/update-profile",
    methods=["POST"]
)
def update_profile():

    if not login_required():

        return redirect(
            url_for("login")
        )

    user_id = session.get("user_id")
    role = session.get("role")

    full_name = request.form.get(
        "name",
        ""
    ).strip()

    email = request.form.get(
        "email",
        ""
    ).strip()

    if not full_name or not email:

        flash(
            "Name and email are required.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    cursor = connection.cursor()

    try:

        # ----------------------------------------------------
        # CHECK DUPLICATE EMAIL
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT user_id
            FROM users
            WHERE email = %s
            AND user_id != %s
            """,
            (
                email,
                user_id
            )
        )

        existing_user = cursor.fetchone()

        if existing_user:

            flash(
                "This email is already being used.",
                "error"
            )

            return redirect(
                url_for("profile")
            )

        # ----------------------------------------------------
        # UPDATE USERS
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE users
            SET
                full_name = %s,
                email = %s
            WHERE user_id = %s
            """,
            (
                full_name,
                email,
                user_id
            )
        )

        # ----------------------------------------------------
        # UPDATE STUDENT
        # ----------------------------------------------------

        if role == "student":

            roll = request.form.get(
                "roll",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            department = request.form.get(
                "department",
                ""
            ).strip()

            graduation = request.form.get(
                "graduation",
                ""
            ).strip()

            year_value = (
                int(graduation)
                if graduation.isdigit()
                else None
            )

            cursor.execute(
                """
                UPDATE students
                SET
                    roll_number = %s,
                    branch = %s,
                    year = %s,
                    phone = %s
                WHERE user_id = %s
                """,
                (
                    roll or None,
                    department or None,
                    year_value,
                    phone or None,
                    user_id
                )
            )

        # ----------------------------------------------------
        # UPDATE COMPANY
        # ----------------------------------------------------

        elif role == "company":

            company_name = request.form.get(
                "company_name",
                ""
            ).strip()

            industry = request.form.get(
                "industry",
                ""
            ).strip()

            location = request.form.get(
                "location",
                ""
            ).strip()

            website = request.form.get(
                "website",
                ""
            ).strip()

            description = request.form.get(
                "description",
                ""
            ).strip()

            cursor.execute(
                """
                UPDATE companies
                SET
                    company_name = %s,
                    industry = %s,
                    location = %s,
                    website = %s,
                    description = %s
                WHERE user_id = %s
                """,
                (
                    company_name,
                    industry or None,
                    location or None,
                    website or None,
                    description or None,
                    user_id
                )
            )

        connection.commit()

        session["full_name"] = full_name
        session["email"] = email

        flash(
            "Profile updated successfully.",
            "success"
        )

        return redirect(
            url_for("profile")
        )

    except Error as e:

        connection.rollback()

        print(
            "UPDATE PROFILE ERROR:",
            e
        )

        flash(
            "Unable to update profile.",
            "error"
        )

        return redirect(
            url_for("profile")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# RESUME ANALYZER COMPATIBILITY ROUTE
# ============================================================

@app.route("/resumee")
def resumee():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return redirect(
        url_for("resume_bp.resume_home")
    )


# ============================================================
# RESUME CREATOR
# ============================================================

@app.route("/resume")
def resume():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="resume.html"
    )


# ============================================================
# COMPANIES
# ============================================================

@app.route("/companies")
def companies():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="companies.html"
    )


# ============================================================
# PLACEMENT DRIVES
# ============================================================

@app.route("/placement-drives")
def placement_drives():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="placement_drives.html"
    )


# ============================================================
# APPLICATIONS
# ============================================================

@app.route("/applications")
def applications():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="applications.html"
    )


# ============================================================
# INTERVIEWS
# ============================================================

@app.route("/interviewss")
def interviewss():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="interviews.html"
    )


# ============================================================
# RESULTS
# ============================================================

@app.route("/results")
def results():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="results.html"
    )


# ============================================================
# STUDENT MANAGEMENT
# ============================================================

@app.route("/students")
def student_management():

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.roll_number AS roll_no,
                u.full_name,
                u.email,
                s.phone,
                s.branch,
                s.year,
                0 AS cgpa,
                0 AS backlogs
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.user_id
            WHERE u.role = 'student'
            ORDER BY s.student_id DESC
            """
        )

        students = cursor.fetchall()

        statistics = calculate_student_statistics(
            students
        )

        return render_template(
            "homepage.html",
            page="student_management.html",
            students=students,
            statistics=statistics
        )

    except Error as e:

        print(
            "STUDENT MANAGEMENT ERROR:",
            e
        )

        flash(
            "Unable to load student records.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# ADD STUDENT
# ============================================================

@app.route(
    "/students/add",
    methods=["GET", "POST"]
)
def add_student():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if request.method == "POST":

        roll_no = request.form.get(
            "roll_no",
            ""
        ).strip()

        full_name = request.form.get(
            "full_name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        branch = request.form.get(
            "branch",
            ""
        ).strip()

        year = request.form.get(
            "year",
            ""
        ).strip()

        password = request.form.get(
            "password",
            "student123"
        )

        if not full_name or not email:

            flash(
                "Full name and email are required.",
                "error"
            )

            return redirect(
                url_for("add_student")
            )

        connection = get_db_connection()

        if connection is None:

            flash(
                "Database connection failed.",
                "error"
            )

            return redirect(
                url_for("add_student")
            )

        cursor = connection.cursor()

        try:

            # Check duplicate email

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE email = %s
                """,
                (email,)
            )

            existing_user = cursor.fetchone()

            if existing_user:

                flash(
                    "A user with this email already exists.",
                    "error"
                )

                return redirect(
                    url_for("add_student")
                )

            year_value = (
                int(year)
                if year.isdigit()
                else None
            )

            password_hash = generate_password_hash(
                password
            )

            # Insert into users

            cursor.execute(
                """
                INSERT INTO users
                (
                    full_name,
                    email,
                    password,
                    role
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    'student'
                )
                """,
                (
                    full_name,
                    email,
                    password_hash
                )
            )

            user_id = cursor.lastrowid

            # Insert into students

            cursor.execute(
                """
                INSERT INTO students
                (
                    user_id,
                    roll_number,
                    branch,
                    year,
                    phone
                )
                VALUES
                (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                """,
                (
                    user_id,
                    roll_no or None,
                    branch or None,
                    year_value,
                    phone or None
                )
            )

            connection.commit()

            flash(
                "Student added successfully.",
                "success"
            )

            return redirect(
                url_for("student_management")
            )

        except Error as e:

            connection.rollback()

            print(
                "ADD STUDENT ERROR:",
                e
            )

            flash(
                "Unable to add student.",
                "error"
            )

            return redirect(
                url_for("add_student")
            )

        finally:

            cursor.close()
            connection.close()

    return render_template(
        "homepage.html",
        page="add_student.html"
    )


# ============================================================
# SEARCH STUDENTS
# ============================================================

@app.route(
    "/students/search",
    methods=["GET", "POST"]
)
def search_students():

    if not login_required():

        return redirect(
            url_for("login")
        )

    search_text = request.values.get(
        "search",
        ""
    ).strip()

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        if search_text:

            search_pattern = (
                "%" + search_text + "%"
            )

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.roll_number AS roll_no,
                    u.full_name,
                    u.email,
                    s.phone,
                    s.branch,
                    s.year,
                    0 AS cgpa,
                    0 AS backlogs
                FROM students s
                INNER JOIN users u
                    ON s.user_id = u.user_id
                WHERE u.role = 'student'
                AND (
                    s.roll_number LIKE %s
                    OR u.full_name LIKE %s
                    OR u.email LIKE %s
                    OR s.branch LIKE %s
                    OR s.phone LIKE %s
                )
                ORDER BY s.student_id DESC
                """,
                (
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern,
                    search_pattern
                )
            )

        else:

            cursor.execute(
                """
                SELECT
                    s.student_id,
                    s.roll_number AS roll_no,
                    u.full_name,
                    u.email,
                    s.phone,
                    s.branch,
                    s.year,
                    0 AS cgpa,
                    0 AS backlogs
                FROM students s
                INNER JOIN users u
                    ON s.user_id = u.user_id
                WHERE u.role = 'student'
                ORDER BY s.student_id DESC
                """
            )

        students = cursor.fetchall()

        statistics = calculate_student_statistics(
            students
        )

        return render_template(
            "homepage.html",
            page="student_management.html",
            students=students,
            statistics=statistics,
            search_text=search_text
        )

    except Error as e:

        print(
            "SEARCH STUDENTS ERROR:",
            e
        )

        flash(
            "Unable to search students.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# VIEW STUDENT
# ============================================================

@app.route(
    "/students/view/<int:student_id>"
)
def view_student(student_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.user_id,
                s.roll_number AS roll_no,
                u.full_name,
                u.email,
                s.phone,
                s.branch,
                s.year,
                s.dob,
                s.gender,
                s.address,
                0 AS cgpa,
                0 AS backlogs
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.user_id
            WHERE s.student_id = %s
            AND u.role = 'student'
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("student_management")
            )

        return render_template(
            "homepage.html",
            page="view_student.html",
            student=student
        )

    except Error as e:

        print(
            "VIEW STUDENT ERROR:",
            e
        )

        flash(
            "Unable to load student details.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# EDIT STUDENT
# ============================================================

@app.route(
    "/students/edit/<int:student_id>",
    methods=["GET", "POST"]
)
def edit_student(student_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        # ----------------------------------------------------
        # UPDATE
        # ----------------------------------------------------

        if request.method == "POST":

            roll_no = request.form.get(
                "roll_no",
                ""
            ).strip()

            full_name = request.form.get(
                "full_name",
                ""
            ).strip()

            email = request.form.get(
                "email",
                ""
            ).strip()

            phone = request.form.get(
                "phone",
                ""
            ).strip()

            branch = request.form.get(
                "branch",
                ""
            ).strip()

            year = request.form.get(
                "year",
                ""
            ).strip()

            if not full_name or not email:

                flash(
                    "Full name and email are required.",
                    "error"
                )

                return redirect(
                    url_for(
                        "edit_student",
                        student_id=student_id
                    )
                )

            # Get user_id

            cursor.execute(
                """
                SELECT user_id
                FROM students
                WHERE student_id = %s
                """,
                (student_id,)
            )

            student_record = cursor.fetchone()

            if student_record is None:

                flash(
                    "Student not found.",
                    "error"
                )

                return redirect(
                    url_for("student_management")
                )

            user_id = student_record["user_id"]

            # Check duplicate email

            cursor.execute(
                """
                SELECT user_id
                FROM users
                WHERE email = %s
                AND user_id != %s
                """,
                (
                    email,
                    user_id
                )
            )

            duplicate_email = cursor.fetchone()

            if duplicate_email:

                flash(
                    "This email is already being used.",
                    "error"
                )

                return redirect(
                    url_for(
                        "edit_student",
                        student_id=student_id
                    )
                )

            year_value = (
                int(year)
                if year.isdigit()
                else None
            )

            # Update users

            cursor.execute(
                """
                UPDATE users
                SET
                    full_name = %s,
                    email = %s
                WHERE user_id = %s
                """,
                (
                    full_name,
                    email,
                    user_id
                )
            )

            # Update students

            cursor.execute(
                """
                UPDATE students
                SET
                    roll_number = %s,
                    branch = %s,
                    year = %s,
                    phone = %s
                WHERE student_id = %s
                """,
                (
                    roll_no or None,
                    branch or None,
                    year_value,
                    phone or None,
                    student_id
                )
            )

            connection.commit()

            flash(
                "Student updated successfully.",
                "success"
            )

            return redirect(
                url_for(
                    "view_student",
                    student_id=student_id
                )
            )

        # ----------------------------------------------------
        # LOAD STUDENT
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                s.student_id,
                s.user_id,
                s.roll_number AS roll_no,
                u.full_name,
                u.email,
                s.phone,
                s.branch,
                s.year,
                s.dob,
                s.gender,
                s.address,
                0 AS cgpa,
                0 AS backlogs
            FROM students s
            INNER JOIN users u
                ON s.user_id = u.user_id
            WHERE s.student_id = %s
            AND u.role = 'student'
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("student_management")
            )

        return render_template(
            "homepage.html",
            page="edit_student.html",
            student=student
        )

    except Error as e:

        connection.rollback()

        print(
            "EDIT STUDENT ERROR:",
            e
        )

        flash(
            "Unable to update student.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# DELETE STUDENT
# ============================================================

@app.route(
    "/students/delete/<int:student_id>",
    methods=["GET", "POST"]
)
def delete_student(student_id):

    if not login_required():

        return redirect(
            url_for("login")
        )

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute(
            """
            SELECT user_id
            FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        student = cursor.fetchone()

        if student is None:

            flash(
                "Student not found.",
                "error"
            )

            return redirect(
                url_for("student_management")
            )

        user_id = student["user_id"]

        # ----------------------------------------------------
        # DELETE STUDENT PROFILE
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM students
            WHERE student_id = %s
            """,
            (student_id,)
        )

        # ----------------------------------------------------
        # DELETE USER ACCOUNT
        # ----------------------------------------------------

        cursor.execute(
            """
            DELETE FROM users
            WHERE user_id = %s
            AND role = 'student'
            """,
            (user_id,)
        )

        connection.commit()

        flash(
            "Student deleted successfully.",
            "success"
        )

        return redirect(
            url_for("student_management")
        )

    except Error as e:

        connection.rollback()

        print(
            "DELETE STUDENT ERROR:",
            e
        )

        flash(
            "Unable to delete student. The student may have related placement records.",
            "error"
        )

        return redirect(
            url_for("student_management")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# STUDENT STATISTICS
# ============================================================

def calculate_student_statistics(students):

    total_students = len(students)

    cse_students = sum(
        1
        for student in students
        if str(
            student.get("branch") or ""
        ).upper() == "CSE"
    )

    high_cgpa_students = sum(
        1
        for student in students
        if float(
            student.get("cgpa") or 0
        ) >= 7
    )

    no_backlog_students = sum(
        1
        for student in students
        if int(
            student.get("backlogs") or 0
        ) == 0
    )

    return {
        "total_students": total_students,
        "cse_students": cse_students,
        "high_cgpa_students": high_cgpa_students,
        "no_backlog_students": no_backlog_students
    }


# ============================================================
# USER MANAGEMENT
# ============================================================

@app.route("/user-management")
def user_management():

    if not login_required():

        return redirect(
            url_for("login")
        )

    if session.get("role") != "admin":

        flash(
            "Access denied.",
            "error"
        )

        return redirect(
            url_for("dashboard")
        )

    return render_template(
        "homepage.html",
        page="user_management.html"
    )


# ============================================================
# COMPANY MANAGEMENT
# ============================================================

@app.route("/company_management")
def company_management():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="company.html"
    )


# ============================================================
# DRIVE MANAGEMENT
# ============================================================

@app.route("/drive-management")
def drive_management():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="drive.html"
    )


# ============================================================
# REPORTS & ANALYTICS
# ============================================================

@app.route("/reports-analytics")
def reports_analytics():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="reports_analytics.html"
    )


# ============================================================
# APTITUDE
# ============================================================

@app.route("/aptitude")
def aptitude():

    if not login_required():

        return redirect(
            url_for("login")
        )

    years = [
        2025,
        2024,
        2023
    ]

    return render_template(
        "homepage.html",
        page="aptitude.html",
        years=years
    )


# ============================================================
# APTITUDE TEST
# ============================================================

@app.route("/test/<int:year>")
def test(year):

    if not login_required():

        return redirect(
            url_for("login")
        )

    return f"You selected the {year} aptitude test."


# ============================================================
# SKILL ASSESSMENT
# ============================================================

@app.route("/skill")
def skill():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="skill_assessment.html"
    )


# ============================================================
# HELP
# ============================================================

@app.route("/help")
def help():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="help.html"
    )


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="about.html"
    )


# ============================================================
# LOGOUT PAGE
# ============================================================

@app.route("/logout")
def logout():

    if not login_required():

        return redirect(
            url_for("login")
        )

    return render_template(
        "homepage.html",
        page="logout.html"
    )


# ============================================================
# CONFIRM LOGOUT
# ============================================================

@app.route("/confirm-logout")
def confirm_logout():

    session.clear()

    return redirect(
        url_for("landing")
    )


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )