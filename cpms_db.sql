-- =========================================================
-- COLLEGE PLACEMENT MANAGEMENT SYSTEM
-- FINAL DATABASE
-- =========================================================

DROP DATABASE IF EXISTS cpms_db;

CREATE DATABASE cpms_db;

USE cpms_db;


-- =========================================================
-- 1. USERS
-- =========================================================

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('student', 'cdpc', 'admin', 'company') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


-- =========================================================
-- 2. STUDENTS
-- =========================================================

CREATE TABLE students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    roll_number VARCHAR(50) UNIQUE,
    branch VARCHAR(100),
    year INT,
    phone VARCHAR(20),
    dob DATE,
    gender VARCHAR(20),
    address TEXT,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 3. COMPANIES
-- =========================================================

CREATE TABLE companies (
    company_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    company_name VARCHAR(150) NOT NULL,
    industry VARCHAR(100),
    location VARCHAR(150),
    website VARCHAR(255),
    description TEXT,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 4. PLACEMENT DRIVES
-- =========================================================

CREATE TABLE placement_drives (
    drive_id INT AUTO_INCREMENT PRIMARY KEY,
    company_id INT NOT NULL,
    job_title VARCHAR(150) NOT NULL,
    description TEXT,
    eligibility VARCHAR(255),
    package VARCHAR(100),
    drive_date DATE,
    application_deadline DATE,
    status VARCHAR(30) DEFAULT 'Open',

    FOREIGN KEY (company_id)
        REFERENCES companies(company_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 5. APPLICATIONS
-- =========================================================

CREATE TABLE applications (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    drive_id INT NOT NULL,
    application_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(50) DEFAULT 'Applied',

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE,

    FOREIGN KEY (drive_id)
        REFERENCES placement_drives(drive_id)
        ON DELETE CASCADE,

    UNIQUE (student_id, drive_id)
);


-- =========================================================
-- 6. INTERVIEWS
-- =========================================================

CREATE TABLE interviews (
    interview_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    interview_date DATE,
    interview_time TIME,
    interview_mode VARCHAR(50),
    meeting_link VARCHAR(255),
    status VARCHAR(50) DEFAULT 'Scheduled',
    feedback TEXT,

    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 7. RESULTS
-- =========================================================

CREATE TABLE results (
    result_id INT AUTO_INCREMENT PRIMARY KEY,
    application_id INT NOT NULL,
    result_status VARCHAR(50),
    package VARCHAR(100),
    result_date DATE,

    FOREIGN KEY (application_id)
        REFERENCES applications(application_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 8. NOTIFICATIONS
-- =========================================================

CREATE TABLE notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(150),
    message TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 9. PROJECTS
-- =========================================================

CREATE TABLE projects (
    project_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    project_name VARCHAR(150) NOT NULL,
    description TEXT,
    technologies VARCHAR(255),
    project_link VARCHAR(255),

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 10. RESUMES
-- =========================================================

CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    file_name VARCHAR(255),
    file_path VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 11. AI RESUME ANALYSIS
-- =========================================================

CREATE TABLE resume_analysis (
    analysis_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT NOT NULL,
    ats_score DECIMAL(5,2),
    extracted_skills TEXT,
    missing_skills TEXT,
    suggestions TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (resume_id)
        REFERENCES resumes(resume_id)
        ON DELETE CASCADE
);


-- =========================================================
-- 12. ASSESSMENTS
-- =========================================================

CREATE TABLE assessments (
    assessment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    assessment_type VARCHAR(50) NOT NULL,
    score DECIMAL(5,2),
    total_marks DECIMAL(5,2),
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (student_id)
        REFERENCES students(student_id)
        ON DELETE CASCADE
);


-- =========================================================
-- VERIFY DATABASE
-- =========================================================

SHOW TABLES;