import re


# ==========================================================
# SKILL DATABASE
# ==========================================================

SKILLS = [

    # Programming
    "python",
    "java",
    "c++",
    "c#",
    "javascript",
    "typescript",
    "c",

    # Web Development
    "html",
    "css",
    "react",
    "angular",
    "node.js",
    "flask",
    "django",

    # Databases
    "sql",
    "mysql",
    "postgresql",
    "mongodb",
    "oracle",

    # Data Analytics
    "excel",
    "power bi",
    "tableau",
    "pandas",
    "numpy",
    "matplotlib",
    "seaborn",
    "data analysis",
    "statistics",

    # AI / ML
    "artificial intelligence",
    "machine learning",
    "deep learning",
    "natural language processing",
    "nlp",
    "tensorflow",
    "pytorch",
    "scikit-learn",

    # Cloud
    "aws",
    "azure",
    "google cloud",

    # Tools
    "git",
    "github",
    "docker",
    "linux",

    # Other
    "rest api",
    "api",
    "problem solving",
    "communication",
    "teamwork"

]


# ==========================================================
# NORMALIZE TEXT
# ==========================================================

def normalize_text(text):

    text = text.lower()

    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ==========================================================
# DETECT SKILLS
# ==========================================================

def detect_skills(text):

    text = normalize_text(
        text
    )

    detected = []


    for skill in SKILLS:

        pattern = (
            r"(?<!\w)"
            + re.escape(skill)
            + r"(?!\w)"
        )


        if re.search(
            pattern,
            text
        ):

            detected.append(
                skill
            )


    return sorted(
        set(detected)
    )


# ==========================================================
# DETECT RESUME SECTIONS
# ==========================================================

def detect_sections(text):

    text = normalize_text(
        text
    )


    sections = {

        "Contact Information": [

            "email",
            "phone",
            "linkedin",
            "github"

        ],

        "Professional Summary": [

            "summary",
            "professional summary",
            "objective",
            "profile"

        ],

        "Education": [

            "education",
            "academic",
            "qualification",
            "b.tech",
            "bachelor",
            "degree"

        ],

        "Technical Skills": [

            "skills",
            "technical skills",
            "technical skill",
            "technologies"

        ],

        "Projects": [

            "projects",
            "project"

        ],

        "Experience": [

            "experience",
            "work experience",
            "professional experience",
            "internship",
            "internships"

        ],

        "Certifications": [

            "certification",
            "certifications",
            "certificate"

        ],

        "Achievements": [

            "achievements",
            "awards",
            "honors"

        ]

    }


    found = {}


    for section, keywords in sections.items():

        found[section] = any(

            keyword in text

            for keyword in keywords

        )


    return found


# ==========================================================
# SECTION SCORE
# ==========================================================

def calculate_section_score(
    sections
):

    weights = {

        "Contact Information": 10,

        "Professional Summary": 10,

        "Education": 15,

        "Technical Skills": 20,

        "Projects": 20,

        "Experience": 15,

        "Certifications": 5,

        "Achievements": 5

    }


    score = 0


    for section, weight in weights.items():

        if sections.get(section):

            score += weight


    return score


# ==========================================================
# ATS SCORE
# ==========================================================

def calculate_ats_score(
    text,
    detected_skills,
    sections
):

    score = 0


    # ------------------------------------------------------
    # CONTACT
    # ------------------------------------------------------

    if sections[
        "Contact Information"
    ]:

        score += 15


    # ------------------------------------------------------
    # IMPORTANT SECTIONS
    # ------------------------------------------------------

    important_sections = [

        "Education",

        "Technical Skills",

        "Projects",

        "Experience"

    ]


    present_sections = sum(

        sections.get(
            section,
            False
        )

        for section
        in important_sections

    )


    score += int(

        (
            present_sections
            /
            len(important_sections)
        )
        * 40

    )


    # ------------------------------------------------------
    # SKILLS
    # ------------------------------------------------------

    skill_count = len(
        detected_skills
    )


    if skill_count >= 10:

        score += 25

    elif skill_count >= 7:

        score += 22

    elif skill_count >= 5:

        score += 18

    elif skill_count >= 3:

        score += 12

    else:

        score += 5


    # ------------------------------------------------------
    # RESUME LENGTH
    # ------------------------------------------------------

    word_count = len(
        text.split()
    )


    if 300 <= word_count <= 1200:

        score += 20

    elif 150 <= word_count <= 1500:

        score += 10


    return min(
        score,
        100
    )


# ==========================================================
# RESUME SCORE
# ==========================================================

def calculate_resume_score(

    section_score,

    skills_count,

    ats_score

):

    skills_score = min(

        skills_count * 5,

        100

    )


    score = (

        section_score * 0.40

        +

        skills_score * 0.25

        +

        ats_score * 0.35

    )


    return round(

        min(
            score,
            100
        ),

        2

    )


# ==========================================================
# RESUME SUMMARY
# ==========================================================

def generate_summary(
    analysis
):

    score = analysis[
        "resume_score"
    ]


    if score >= 85:

        return (
            "Excellent resume structure. "
            "Your resume appears well prepared "
            "for placement applications."
        )


    elif score >= 70:

        return (
            "Good resume with a strong foundation. "
            "A few improvements can make it more "
            "competitive for placement opportunities."
        )


    elif score >= 50:

        return (
            "Your resume has a basic structure, "
            "but several areas should be improved "
            "before applying for competitive roles."
        )


    else:

        return (
            "Your resume needs significant improvement "
            "in structure, skills and content."
        )


# ==========================================================
# SUGGESTIONS
# ==========================================================

def generate_suggestions(
    analysis
):

    suggestions = []


    sections = analysis[
        "sections"
    ]


    skills = analysis[
        "detected_skills"
    ]


    # ------------------------------------------------------
    # SUMMARY
    # ------------------------------------------------------

    if not sections[
        "Professional Summary"
    ]:

        suggestions.append(

            "Add a professional summary "
            "that clearly describes your "
            "career objective and technical strengths."

        )


    # ------------------------------------------------------
    # PROJECTS
    # ------------------------------------------------------

    if not sections[
        "Projects"
    ]:

        suggestions.append(

            "Add 2-3 relevant technical projects "
            "with technologies used and measurable results."

        )


    # ------------------------------------------------------
    # EXPERIENCE
    # ------------------------------------------------------

    if not sections[
        "Experience"
    ]:

        suggestions.append(

            "If you have completed internships "
            "or practical experience, add an "
            "Experience section."

        )


    # ------------------------------------------------------
    # CERTIFICATIONS
    # ------------------------------------------------------

    if not sections[
        "Certifications"
    ]:

        suggestions.append(

            "Add relevant technical certifications "
            "to strengthen your profile."

        )


    # ------------------------------------------------------
    # ACHIEVEMENTS
    # ------------------------------------------------------

    if not sections[
        "Achievements"
    ]:

        suggestions.append(

            "Add achievements, hackathons, "
            "coding contests or academic accomplishments "
            "if applicable."

        )


    # ------------------------------------------------------
    # GITHUB
    # ------------------------------------------------------

    if "github" not in analysis[
        "text"
    ]:

        suggestions.append(

            "Add your GitHub profile so recruiters "
            "can review your technical projects."

        )


    # ------------------------------------------------------
    # LINKEDIN
    # ------------------------------------------------------

    if "linkedin" not in analysis[
        "text"
    ]:

        suggestions.append(

            "Add your LinkedIn profile "
            "to improve your professional presence."

        )


    # ------------------------------------------------------
    # SKILLS
    # ------------------------------------------------------

    if len(skills) < 5:

        suggestions.append(

            "Add more relevant technical skills "
            "that match your target job role."

        )


    # ------------------------------------------------------
    # SCORE
    # ------------------------------------------------------

    if analysis[
        "resume_score"
    ] < 60:

        suggestions.append(

            "Focus on improving resume structure, "
            "projects, skills and relevant achievements."

        )


    elif analysis[
        "resume_score"
    ] < 80:

        suggestions.append(

            "Your resume is on the right track. "
            "Tailor your skills and projects "
            "for each placement role."

        )


    else:

        suggestions.append(

            "Your resume has a strong structure. "
            "Continue tailoring it for specific "
            "job descriptions."

        )


    return suggestions


# ==========================================================
# COMPLETE RESUME ANALYSIS
# ==========================================================

def analyze_resume(
    text
):

    normalized_text = normalize_text(
        text
    )


    detected_skills = detect_skills(
        normalized_text
    )


    sections = detect_sections(
        normalized_text
    )


    section_score = calculate_section_score(
        sections
    )


    ats_score = calculate_ats_score(

        normalized_text,

        detected_skills,

        sections

    )


    resume_score = calculate_resume_score(

        section_score,

        len(detected_skills),

        ats_score

    )


    skills_score = min(

        len(detected_skills) * 5,

        100

    )


    analysis = {

        "text": normalized_text,

        "detected_skills":
            detected_skills,

        "sections":
            sections,

        "section_score":
            section_score,

        "ats_score":
            ats_score,

        "skills_score":
            skills_score,

        "resume_score":
            resume_score

    }


    analysis[
        "summary"
    ] = generate_summary(
        analysis
    )


    return analysis


# ==========================================================
# JOB DESCRIPTION MATCHING
# ==========================================================

def match_job_description(

    resume_text,

    job_description

):

    resume_skills = detect_skills(
        resume_text
    )


    job_skills = detect_skills(
        job_description
    )


    if not job_skills:

        return {

            "match_percentage": 0,

            "matched_skills": [],

            "missing_skills": [],

            "recommendation":
                "No recognizable technical skills "
                "were found in the Job Description."

        }


    matched_skills = [

        skill

        for skill in job_skills

        if skill in resume_skills

    ]


    missing_skills = [

        skill

        for skill in job_skills

        if skill not in resume_skills

    ]


    match_percentage = round(

        (
            len(matched_skills)
            /
            len(job_skills)
        )
        * 100,

        2

    )


    if match_percentage >= 80:

        recommendation = (
            "Strong Match"
        )


    elif match_percentage >= 60:

        recommendation = (
            "Good Match"
        )


    elif match_percentage >= 40:

        recommendation = (
            "Moderate Match"
        )


    else:

        recommendation = (
            "Low Match"
        )


    return {

        "match_percentage":
            match_percentage,

        "matched_skills":
            matched_skills,

        "missing_skills":
            missing_skills,

        "recommendation":
            recommendation

    }