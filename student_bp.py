# ============================================================
# STUDENT MANAGEMENT
# ============================================================

@app.route("/students")
def student_management():

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>Database connection failed.</h2>
        <p>Please check MySQL and placement_db.</p>
        """, 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                full_name,
                email,
                phone,
                branch,
                year,
                cgpa,
                backlogs
            FROM students
            ORDER BY student_id DESC
        """)

        students = cursor.fetchall()

        # IMPORTANT FIX
        students = normalize_students(
            students
        )

        statistics = calculate_student_statistics(
            students
        )

        return render_template(
            "homepage.html",
            page="student_management.html",
            students=students,
            search="",
            **statistics
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>Database Error</h2>
        <p>{error}</p>
        """, 500

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

    if request.method == "GET":

        return render_template(
            "homepage.html",
            page="add_student.html"
        )

    connection = get_db_connection()

    if connection is None:

        flash(
            "Database connection failed."
        )

        return redirect(
            url_for("student_management")
        )

    cursor = connection.cursor()

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

    cgpa = request.form.get(
        "cgpa",
        ""
    ).strip()

    backlogs = request.form.get(
        "backlogs",
        "0"
    ).strip()

    if not roll_no:

        flash("Roll number is required.")

        cursor.close()
        connection.close()

        return redirect(
            url_for("add_student")
        )

    if not full_name:

        flash("Student name is required.")

        cursor.close()
        connection.close()

        return redirect(
            url_for("add_student")
        )

    if not email:

        flash("Email is required.")

        cursor.close()
        connection.close()

        return redirect(
            url_for("add_student")
        )

    try:

        year_value = int(year)

        cgpa_value = float(cgpa)

        backlogs_value = int(
            backlogs or 0
        )

    except ValueError:

        flash(
            "Year, CGPA and backlogs must contain valid numbers."
        )

        cursor.close()
        connection.close()

        return redirect(
            url_for("add_student")
        )

    if cgpa_value < 0 or cgpa_value > 10:

        flash(
            "CGPA must be between 0 and 10."
        )

        cursor.close()
        connection.close()

        return redirect(
            url_for("add_student")
        )

    if backlogs_value < 0:

        flash(
            "Backlogs cannot be negative."
        )

        cursor.close()
        connection.close()

        return redirect(
            url_for("add_student")
        )

    try:

        # Check duplicate roll number

        cursor.execute("""
            SELECT student_id
            FROM students
            WHERE roll_no = %s
        """, (
            roll_no,
        ))

        existing = cursor.fetchone()

        if existing:

            flash(
                "Roll number already exists."
            )

            cursor.close()
            connection.close()

            return redirect(
                url_for("add_student")
            )

        cursor.execute("""
            INSERT INTO students
            (
                roll_no,
                full_name,
                email,
                phone,
                branch,
                year,
                cgpa,
                backlogs
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
        """, (
            roll_no,
            full_name,
            email,
            phone,
            branch,
            year_value,
            cgpa_value,
            backlogs_value
        ))

        connection.commit()

        flash(
            "Student added successfully."
        )

        return redirect(
            url_for("student_management")
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to add student: {error}"
        )

        return redirect(
            url_for("add_student")
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# SEARCH STUDENTS
# ============================================================

@app.route(
    "/students/search",
    methods=["GET", "POST"]
)
def search_students():

    search = request.args.get(
        "search",
        ""
    ).strip()

    if request.method == "POST":

        search = request.form.get(
            "search",
            ""
        ).strip()

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>Database connection failed.</h2>
        """, 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        if search:

            search_value = (
                "%"
                + search
                + "%"
            )

            cursor.execute("""
                SELECT
                    student_id,
                    roll_no,
                    full_name,
                    email,
                    phone,
                    branch,
                    year,
                    cgpa,
                    backlogs
                FROM students
                WHERE
                    roll_no LIKE %s
                    OR full_name LIKE %s
                    OR email LIKE %s
                    OR phone LIKE %s
                    OR branch LIKE %s
                ORDER BY student_id DESC
            """, (
                search_value,
                search_value,
                search_value,
                search_value,
                search_value
            ))

        else:

            cursor.execute("""
                SELECT
                    student_id,
                    roll_no,
                    full_name,
                    email,
                    phone,
                    branch,
                    year,
                    cgpa,
                    backlogs
                FROM students
                ORDER BY student_id DESC
            """)

        students = cursor.fetchall()

        # IMPORTANT FIX
        students = normalize_students(
            students
        )

        statistics = calculate_student_statistics(
            students
        )

        return render_template(
            "homepage.html",
            page="student_management.html",
            students=students,
            search=search,
            **statistics
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>Database Error</h2>
        <p>{error}</p>
        """, 500

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

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>Database connection failed.</h2>
        """, 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                full_name,
                email,
                phone,
                branch,
                year,
                cgpa,
                backlogs
            FROM students
            WHERE student_id = %s
        """, (
            student_id,
        ))

        student = cursor.fetchone()

        if student is None:

            return """
            <h2>Student not found.</h2>
            """, 404

        student = normalize_student(
            student
        )

        return render_template(
            "homepage.html",
            page="view_student.html",
            student=student
        )

    except mysql.connector.Error as error:

        return f"""
        <h2>Database Error</h2>
        <p>{error}</p>
        """, 500

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

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>Database connection failed.</h2>
        """, 500

    cursor = connection.cursor(
        dictionary=True
    )

    try:

        cursor.execute("""
            SELECT
                student_id,
                roll_no,
                full_name,
                email,
                phone,
                branch,
                year,
                cgpa,
                backlogs
            FROM students
            WHERE student_id = %s
        """, (
            student_id,
        ))

        student = cursor.fetchone()

        if student is None:

            return """
            <h2>Student not found.</h2>
            """, 404

        student = normalize_student(
            student
        )

        if request.method == "GET":

            return render_template(
                "homepage.html",
                page="edit_student.html",
                student=student
            )

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

        cgpa = request.form.get(
            "cgpa",
            ""
        ).strip()

        backlogs = request.form.get(
            "backlogs",
            "0"
        ).strip()

        try:

            year_value = int(year)

            cgpa_value = float(cgpa)

            backlogs_value = int(
                backlogs or 0
            )

        except ValueError:

            flash(
                "Please enter valid student details."
            )

            return redirect(
                url_for(
                    "edit_student",
                    student_id=student_id
                )
            )

        if cgpa_value < 0 or cgpa_value > 10:

            flash(
                "CGPA must be between 0 and 10."
            )

            return redirect(
                url_for(
                    "edit_student",
                    student_id=student_id
                )
            )

        cursor.execute("""
            UPDATE students
            SET
                roll_no = %s,
                full_name = %s,
                email = %s,
                phone = %s,
                branch = %s,
                year = %s,
                cgpa = %s,
                backlogs = %s
            WHERE student_id = %s
        """, (
            roll_no,
            full_name,
            email,
            phone,
            branch,
            year_value,
            cgpa_value,
            backlogs_value,
            student_id
        ))

        connection.commit()

        flash(
            "Student updated successfully."
        )

        return redirect(
            url_for("student_management")
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to update student: {error}"
        )

        return redirect(
            url_for(
                "edit_student",
                student_id=student_id
            )
        )

    finally:

        cursor.close()
        connection.close()


# ============================================================
# DELETE STUDENT
# ============================================================
# Supports GET and POST because your current HTML uses
# a normal href link.
# ============================================================

@app.route(
    "/students/delete/<int:student_id>",
    methods=["GET", "POST"]
)
def delete_student(student_id):

    connection = get_db_connection()

    if connection is None:

        return """
        <h2>Database connection failed.</h2>
        """, 500

    cursor = connection.cursor()

    try:

        cursor.execute("""
            DELETE FROM students
            WHERE student_id = %s
        """, (
            student_id,
        ))

        connection.commit()

        flash(
            "Student deleted successfully."
        )

    except mysql.connector.Error as error:

        connection.rollback()

        flash(
            f"Unable to delete student: {error}"
        )

    finally:

        cursor.close()
        connection.close()

    return redirect(
        url_for("student_management")
    )

