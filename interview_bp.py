from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector

interview_bp = Blueprint('interview_bp', __name__)

# ============================================================
# DATABASE CONNECTION
# ============================================================
try:
    db = mysql.connector.connect(
        host="localhost",
        user="placement_user",
        password="Sivaleela@19",
        database="placement_db"
    )
    cursor = db.cursor(dictionary=True)
    print("Interview BP: MySQL database connected successfully.")
except mysql.connector.Error as error:
    print("Interview BP: MySQL connection failed:", error)
    db = None
    cursor = None


# ============================================================
# INTERVIEW MANAGEMENT HOME
# ============================================================
@interview_bp.route("/interviews")
def interview_management():
    if db is None:
        return "<h2>Database connection failed. Check MySQL configuration.</h2>", 500

    try:
        cursor.execute("""
            SELECT * FROM interviews
            ORDER BY interview_date ASC, interview_time ASC
        """)
        interviews = cursor.fetchall()
    except mysql.connector.Error as error:
        return f"<h2>Database Error</h2><p>{error}</p>", 500

    return render_template("homepage.html", page="interview_management.html", interviews=interviews)


# ============================================================
# SCHEDULE INTERVIEW
# ============================================================
@interview_bp.route("/interviews/schedule", methods=["GET", "POST"])
def schedule_interview():
    if db is None:
        return "<h2>Database connection failed.</h2>", 500

    if request.method == "GET":
        return render_template("homepage.html", page="schedule_interview.html")

    student_name = request.form.get("student_name", "").strip()
    company_name = request.form.get("company_name", "").strip()
    round_name = request.form.get("round_name", "").strip()
    interviewer_name = request.form.get("interviewer_name", "").strip()
    interview_date = request.form.get("interview_date", "").strip()
    interview_time = request.form.get("interview_time", "").strip()
    interview_mode = request.form.get("interview_mode", "").strip()
    meeting_link = request.form.get("meeting_link", "").strip()
    location = request.form.get("location", "").strip()
    remarks = request.form.get("remarks", "").strip()

    if not student_name or not company_name or not round_name or not interview_date or not interview_time or not interview_mode:
        flash("Please fill in all required fields.")
        return redirect(url_for("interview_bp.schedule_interview"))

    try:
        cursor.execute("""
            INSERT INTO interviews
            (student_name, company_name, round_name, interviewer_name, interview_date, interview_time, interview_mode, meeting_link, location, remarks, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (student_name, company_name, round_name, interviewer_name, interview_date, interview_time, interview_mode, meeting_link, location, remarks, "Scheduled"))
        db.commit()
        flash("Interview scheduled successfully.")
        return redirect(url_for("interview_bp.interview_management"))
    except mysql.connector.Error as error:
        db.rollback()
        flash(f"Unable to schedule interview: {error}")
        return redirect(url_for("interview_bp.schedule_interview"))


# ============================================================
# INTERVIEW DETAILS
# ============================================================
@interview_bp.route("/interviews/<int:interview_id>")
def interview_details(interview_id):
    if db is None:
        return "<h2>Database connection failed.</h2>", 500

    try:
        cursor.execute("SELECT * FROM interviews WHERE interview_id = %s", (interview_id,))
        interview = cursor.fetchone()
    except mysql.connector.Error as error:
        return f"<h2>Database Error</h2><p>{error}</p>", 500

    if interview is None:
        return "<h2>Interview not found.</h2>", 404

    return render_template("homepage.html", page="interview_details.html", interview=interview)


# ============================================================
# INTERVIEW EVALUATION
# ============================================================
@interview_bp.route("/interviews/<int:interview_id>/evaluate", methods=["GET", "POST"])
def interview_evaluation(interview_id):
    if db is None:
        return "<h2>Database connection failed.</h2>", 500

    try:
        cursor.execute("SELECT * FROM interviews WHERE interview_id = %s", (interview_id,))
        interview = cursor.fetchone()
    except mysql.connector.Error as error:
        return f"<h2>Database Error</h2><p>{error}</p>", 500

    if interview is None:
        return "<h2>Interview not found.</h2>", 404

    if request.method == "GET":
        return render_template("homepage.html", page="interview_evaluation.html", interview=interview)

    try:
        technical_score = float(request.form.get("technical_score", 0))
        communication_score = float(request.form.get("communication_score", 0))
        problem_solving_score = float(request.form.get("problem_solving_score", 0))
        aptitude_score = float(request.form.get("aptitude_score", 0))
    except ValueError:
        flash("Please enter valid numeric scores.")
        return redirect(url_for("interview_bp.interview_evaluation", interview_id=interview_id))

    scores = [technical_score, communication_score, problem_solving_score, aptitude_score]
    if any(score < 0 or score > 100 for score in scores):
        flash("All scores must be between 0 and 100.")
        return redirect(url_for("interview_bp.interview_evaluation", interview_id=interview_id))

    overall_score = sum(scores) / 4
    feedback = request.form.get("feedback", "").strip()
    recommendation = request.form.get("recommendation", "").strip()

    valid_recommendations = {"Selected", "Rejected", "Waitlisted", "Next Round"}
    if recommendation not in valid_recommendations:
        flash("Please select a valid recommendation.")
        return redirect(url_for("interview_bp.interview_evaluation", interview_id=interview_id))

    try:
        cursor.execute("""
            INSERT INTO interview_evaluations
            (interview_id, technical_score, communication_score, problem_solving_score, aptitude_score, overall_score, feedback, recommendation)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (interview_id, technical_score, communication_score, problem_solving_score, aptitude_score, overall_score, feedback, recommendation))

        status = recommendation if recommendation in valid_recommendations else "Completed"
        cursor.execute("UPDATE interviews SET status = %s WHERE interview_id = %s", (status, interview_id))
        db.commit()

        flash("Interview evaluation saved successfully.")
        return redirect(url_for("interview_bp.interview_result", interview_id=interview_id))
    except mysql.connector.Error as error:
        db.rollback()
        flash(f"Unable to save evaluation: {error}")
        return redirect(url_for("interview_bp.interview_evaluation", interview_id=interview_id))


# ============================================================
# INTERVIEW RESULT
# ============================================================
@interview_bp.route("/interviews/<int:interview_id>/result")
def interview_result(interview_id):
    if db is None:
        return "<h2>Database connection failed.</h2>", 500

    try:
        cursor.execute("SELECT * FROM interviews WHERE interview_id = %s", (interview_id,))
        interview = cursor.fetchone()

        cursor.execute("""
            SELECT * FROM interview_evaluations
            WHERE interview_id = %s
            ORDER BY evaluation_id DESC LIMIT 1
        """, (interview_id,))
        evaluation = cursor.fetchone()
    except mysql.connector.Error as error:
        return f"<h2>Database Error</h2><p>{error}</p>", 500

    if interview is None or evaluation is None:
        return "<h2>Interview or evaluation not found.</h2>", 404

    return render_template("homepage.html", page="interview_result.html", interview=interview, evaluation=evaluation)