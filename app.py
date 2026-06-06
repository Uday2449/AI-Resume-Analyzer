from flask import Flask, render_template, request
import os
import pdfplumber
import sqlite3

app = Flask(__name__)

# Create uploads folder
os.makedirs("uploads", exist_ok=True)

# Skills Database
skills_db = [
    "python",
    "javascript",
    "sql",
    "html",
    "css",
    "git",
    "flask",
    "servicenow",
    "java",
    "c",
    "c++"
]

# Job Roles
job_roles = {
    "ServiceNow Developer": [
        "servicenow",
        "javascript",
        "html",
        "css",
        "sql"
    ],
    "Python Developer": [
        "python",
        "sql",
        "git",
        "flask",
        "javascript"
    ],
    "Frontend Developer": [
        "html",
        "css",
        "javascript",
        "git"
    ],
    "Java Developer": [
        "java",
        "sql",
        "git"
    ],
    "Full Stack Developer": [
        "html",
        "css",
        "javascript",
        "python",
        "sql",
        "git",
        "flask"
    ]
}


# Extract text from PDF
def extract_text(pdf_path):

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# Extract skills
def extract_skills(text):

    text = text.lower()

    found_skills = []

    for skill in skills_db:

        if skill in text:
            found_skills.append(skill)

    return found_skills


# ATS Score
def calculate_score(skills):

    return int(
        (len(skills) / len(skills_db)) * 100
    )


# Role Match
def calculate_role_match(
        resume_skills,
        role):

    role_skills = job_roles.get(
        role,
        []
    )

    matched = []
    missing = []

    for skill in role_skills:

        if skill in resume_skills:
            matched.append(skill)

        else:
            missing.append(skill)

    if len(role_skills) == 0:
        score = 0
    else:
        score = int(
            (len(matched) / len(role_skills)) * 100
        )

    return score, matched, missing


# Suggestions
def generate_suggestions(missing_skills):

    suggestions = []

    for skill in missing_skills:

        suggestions.append(
            f"Consider learning {skill}"
        )

    if len(missing_skills) == 0:

        suggestions.append(
            "Excellent! Resume matches the role well."
        )

    return suggestions


# AI Feedback
def ai_feedback(skills, missing_skills):

    strengths = []
    weaknesses = []
    recommendations = []

    if "servicenow" in skills:
        strengths.append(
            "Strong ServiceNow knowledge"
        )

    if "python" in skills:
        strengths.append(
            "Good Python programming skills"
        )

    if "javascript" in skills:
        strengths.append(
            "Good web development experience"
        )

    if "git" in skills:
        strengths.append(
            "Version control knowledge"
        )

    for skill in missing_skills:

        weaknesses.append(
            f"Missing {skill}"
        )

        recommendations.append(
            f"Learn {skill}"
        )

    recommendations.append(
        "Add measurable achievements in projects"
    )

    recommendations.append(
        "Add GitHub project links"
    )

    recommendations.append(
        "Add more technical projects"
    )

    return strengths, weaknesses, recommendations


# Save Analysis
def save_analysis(
        filename,
        role,
        ats_score,
        match_score):

    conn = sqlite3.connect(
        "resume_analyzer.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO analyses
        (
            filename,
            role,
            ats_score,
            match_score
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            filename,
            role,
            ats_score,
            match_score
        )
    )

    conn.commit()
    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():

    message = ""
    resume_text = ""
    skills = []
    score = 0

    job_role = ""

    job_match_score = 0

    matched_skills = []
    missing_skills = []

    suggestions = []

    strengths = []
    weaknesses = []
    recommendations = []

    if request.method == "POST":

        job_role = request.form.get(
            "job_role"
        )

        file = request.files["resume"]

        filepath = os.path.join(
            "uploads",
            file.filename
        )

        file.save(filepath)

        resume_text = extract_text(
            filepath
        )

        skills = extract_skills(
            resume_text
        )

        score = calculate_score(
            skills
        )

        job_match_score, matched_skills, missing_skills = calculate_role_match(
            skills,
            job_role
        )

        suggestions = generate_suggestions(
            missing_skills
        )

        strengths, weaknesses, recommendations = ai_feedback(
            skills,
            missing_skills
        )

        save_analysis(
            file.filename,
            job_role,
            score,
            job_match_score
        )

        message = "Resume Uploaded Successfully!"

    return render_template(
        "index.html",
        message=message,
        resume_text=resume_text,
        skills=skills,
        score=score,
        job_role=job_role,
        job_match_score=job_match_score,
        matched_skills=matched_skills,
        missing_skills=missing_skills,
        suggestions=suggestions,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations
    )


@app.route("/history")
def history():

    conn = sqlite3.connect(
        "resume_analyzer.db"
    )

    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM analyses"
    )

    data = cursor.fetchall()

    conn.close()

    return render_template(
        "history.html",
        data=data
    )


@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("resume_analyzer.db")
    cursor = conn.cursor()

    # Total resumes
    cursor.execute("SELECT COUNT(*) FROM analyses")
    total_resumes = cursor.fetchone()[0]

    # Average ATS
    cursor.execute("SELECT AVG(ats_score) FROM analyses")
    avg_ats = cursor.fetchone()[0]

    if avg_ats is None:
        avg_ats = 0

    # Average Match
    cursor.execute("SELECT AVG(match_score) FROM analyses")
    avg_match = cursor.fetchone()[0]

    if avg_match is None:
        avg_match = 0

    # Role Distribution
    cursor.execute("""
        SELECT role, COUNT(*)
        FROM analyses
        GROUP BY role
    """)

    role_data = cursor.fetchall()

    conn.close()

    labels = []
    values = []

    for row in role_data:
        labels.append(row[0])
        values.append(row[1])

    return render_template(
        "dashboard.html",
        total_resumes=total_resumes,
        avg_ats=round(avg_ats, 2),
        avg_match=round(avg_match, 2),
        labels=labels,
        values=values
    )


if __name__ == "__main__":
    app.run(debug=True)