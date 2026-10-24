import email

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    RedirectResponse
)
from fastapi.templating import Jinja2Templates

from typing import List
from pydantic import BaseModel

from fastapi.staticfiles import StaticFiles

from app.parser import extract_text


from app.text_extractor import extract_text as extract_pdf_text
from app.semantic_matcher import get_ai_score

from app.extractor import (
    extract_email,
    extract_phone,
    extract_skills,
    extract_name
)

from app.matcher import calculate_match
from database.db import conn, cursor, get_candidate

import os
import uuid

from chatbot.rag import ask_resume_chatbot
from chatbot.embeddings import create_embeddings
from chatbot.rag import build_index

chatbot_chunks = None
chatbot_index = None

app = FastAPI()

class ChatRequest(BaseModel):
    message: str

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(directory="templates")


@app.get("/")
def home():
    return FileResponse(
    "templates/index.html"

)

@app.post("/upload")
async def upload_resume(
    resumes: List[UploadFile] = File(...),
    job: UploadFile = File(...)
):

    if job.content_type != "application/pdf":
        return {"error": "Job description must be PDF"}

    print("Total Resumes:", len(resumes))
    print("Job:", job.filename)

    BASE_DIR = os.path.dirname(
        os.path.abspath(__file__)
    )

    resume_folder = os.path.join(
        BASE_DIR,
        "resumes"
    )

    job_folder = os.path.join(
        BASE_DIR,
        "jobs"
    )

    os.makedirs(resume_folder, exist_ok=True)
    os.makedirs(job_folder, exist_ok=True)

    # Save Job File

    job_content = await job.read()

    job_path = os.path.join(
        job_folder,
        f"{uuid.uuid4()}_{job.filename}"
    )

    with open(job_path, "wb") as f:
        f.write(job_content)

    jd_text = extract_text(job_path)

    print("================================")
    print("JOB DESCRIPTION LENGTH =", len(jd_text))
    print("FIRST 1000 CHARACTERS OF JD")
    print(jd_text[:1000])
    print("================================")

    # Clear old leaderboard entries

    cursor.execute(
    "DELETE FROM candidates"
)

    conn.commit()

    results = []

    # Process multiple resumes

    for resume in resumes:

        if resume.content_type != "application/pdf":
            return {"error": "Only PDF resumes allowed"}
        
        content = await resume.read()

        resume_path = os.path.join(
            resume_folder,
            f"{uuid.uuid4()}_{resume.filename}"
        )

        with open(resume_path, "wb") as f:
            f.write(content)

        resume_text = extract_text(
            resume_path
        )

        print("================================")
        print("RESUME LENGTH =", len(resume_text))
        print("FIRST 1000 CHARACTERS OF RESUME")
        print(resume_text[:1000])
        print("================================")

        global chatbot_chunks
        global chatbot_index

        chatbot_chunks = [
            resume_text[i:i + 500]
            for i in range(0, len(resume_text), 500)
        ]

        vectors = create_embeddings(
            chatbot_chunks
        )

        chatbot_index = build_index(
            vectors
        )

        ai_score = get_ai_score(
            resume_text,
            jd_text
        )

        ai_score = float(ai_score)

        print("AI SCORE =", ai_score)
        print("TYPE =", type(ai_score))

        email = extract_email(
            resume_text
        )

        phone = extract_phone(
            resume_text
        )

        skills = extract_skills(
            resume_text
        )

        name = extract_name(
        resume_text
        )


        cursor.execute(
            """
            INSERT INTO candidates
            (name, email, phone, skills, score)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                name,
                email[0] if email else "",
                phone[0] if phone else "",
                ",".join(skills),
                ai_score
            )
        )

        conn.commit()

        results.append({
            "email": email[0] if email else "",
            "phone": phone[0] if phone else "",
            "score": ai_score
        })

    return RedirectResponse(
    url="/leaderboard",
    status_code=303
)

@app.get("/candidates")
def get_candidates():

    cursor.execute(
        "SELECT * FROM candidates"
    )

    rows = cursor.fetchall()

    return {
        "candidates": rows
    }


@app.get("/match")
def match_candidate():

    candidate_skills = [
        "Python",
        "React.js",
        "Node.js",
        "Git"
    ]

    job_skills = [
        "Python",
        "React.js",
        "SQL",
        "AWS"
    ]

    result = calculate_match(
        candidate_skills,
        job_skills
    )

    return {
        "match_score": result["match_score"]
    }


@app.get("/job-match")
def job_match():

    cursor.execute(
        "SELECT * FROM candidates ORDER BY id DESC LIMIT 1"
    )

    candidate = cursor.fetchone()

    if not candidate:
        return {
            "error": "No candidate found"
        }

    candidate_skills = candidate[3].split(",")

    job_skills = [
        "Python",
        "React.js",
        "SQL",
        "AWS"
    ]

    result = calculate_match(
        candidate_skills,
        job_skills
    )

    return {
        "candidate_skills": candidate_skills,
        "job_skills": job_skills,
        "match_score": result["match_score"],
        "matched_skills": result["matched_skills"],
        "missing_skills": result["missing_skills"],
        "recommendation": result["recommendation"]
    }


@app.get("/leaderboard")
def leaderboard():

    cursor.execute("""
    SELECT *
    FROM candidates
    ORDER BY score DESC
    """)

    candidates = cursor.fetchall()

    html = """
    <html>

    <head>

    <title>Candidate Leaderboard</title>

    <style>

    body{
    font-family:'Poppins',sans-serif;
    background:linear-gradient(
        135deg,
        #dbeafe,
        #e9d5ff,
        #f8fafc
    );
    padding:30px;
}

    .container{
    max-width:1100px;
    margin:auto;
    background:white;
    padding:40px;
    border-radius:25px;
    box-shadow:0 20px 50px rgba(0,0,0,0.12);
}

    h1{
    text-align:center;
    font-size:48px;
    color:#1e293b;
    margin-bottom:15px;
}

    table{
    width:100%;
    border-collapse:collapse;
    border-radius:15px;
    overflow:hidden;
    background:white;
}

    th{
    background:linear-gradient(
        135deg,
        #2563eb,
        #7c3aed
    );
    color:white;
    padding:18px;
    font-size:16px;
}

    td{
        padding:15px;
        border:1px solid #ddd;
    }

    tr:nth-child(even){
    background:#f8fafc;
}

tr:hover{
    background:#eef4ff;
}

    </style>

    </head>

    <body>

    <div class="container">

    <h1>🏆 AI Candidate Leaderboard</h1>

<p style="
text-align:center;
color:#64748b;
margin-bottom:30px;
font-size:18px;">
Ranked by AI Match Score
</p>

    <div style="
background:white;
padding:25px;
border-radius:20px;
box-shadow:0 10px 25px rgba(0,0,0,0.08);
">

    <table>

        <tr>
           <th>Rank</th>
           <th>Name</th>
           <th>Skills</th>
           <th>Score</th>
           <th>Action</th> 
        </tr>
    """

    rank = 1

    for candidate in candidates:

        html += f"""
        <tr>
            <td>
{
    "🥇" if rank == 1
    else "🥈" if rank == 2
    else "🥉" if rank == 3
    else rank
}
</td>
            <td>{candidate[1]}</td>
            <td>{candidate[4]}</td>
            <td>{round(candidate[5],2)}%</td>
            <td>
                <a href="/candidate/{candidate[0]}">
                    <button>View Report</button>
                </a>
            </td>
        </tr>
        """

        rank += 1

    html += """

</table>

</div>

<br><br>

<center>

<a href="/">

<button style="
padding:12px 20px;
background:#2563eb;
color:white;
border:none;
border-radius:8px;
cursor:pointer;
font-size:16px;
">

🏠 Back to Upload Page

</button>

</a>

</center>

</div>

</body>

</html>
"""

    return HTMLResponse(content=html)

@app.get("/candidate/{candidate_id}", response_class=HTMLResponse)
def candidate_report(candidate_id: int):

    candidate = get_candidate(candidate_id)
    print("Candidate =", candidate)

    
    
    if candidate is None:
        return HTMLResponse(
        content="<h1>Candidate Not Found</h1>"
    )



    skills = candidate[4].split(",")

    jd_skills = [
    "Python",
    "React.js",
    "AWS",
    "Docker",
    "Kubernetes",
    "HTML",
    "CSS"
]

    matched_skills = []

    for skill in skills:

        if skill.strip() in jd_skills:

            matched_skills.append(skill.strip())

    missing_skills = []

    for skill in jd_skills:

        if skill not in matched_skills:

            missing_skills.append(skill)

    score = candidate[5]

    if score >= 80:
         recommendation = "Strong Match"

    elif score >= 50:
         recommendation = "Consider"

    else:
         recommendation = "Reject"

    skills_html = ""

    matched_html = ""

    for skill in matched_skills:

        matched_html += f"""
        <span class="matched">
            ✅ {skill}
        </span>
        """

        missing_html = "" 

        for skill in missing_skills:

            missing_html += f"""
            <span class="missing">
                ❌ {skill}
            </span>
            """

    for skill in skills:

        skills_html += f"""
        <span class="skill">
            {skill.strip()}
        </span>
        """

    if recommendation == "Strong Match":
        recommendation_class = "green"

    elif recommendation == "Consider":
        recommendation_class = "orange"

    else:
        recommendation_class = "red"

    html = f"""
    <html>

<head>

<title>Candidate Report</title>

<style>

body{{
    background:#f4f7fa;
    font-family:Arial,sans-serif;
    padding:40px;
}}

.card{{
    max-width:800px;
    margin:auto;
    background:white;
}}

h1{{
    color:#2563eb;
}}

.score{{
    background:#22c55e;
    color:white;
    width:200px;
    padding:15px;
    border-radius:10px;
    text-align:center;
    font-size:24px;
    font-weight:bold;
}}

.section{{
    margin-top:20px;
}}

.recommendation{{
    display:inline-block;
    background:#dc2626;
    color:white;
    padding:10px 20px;
    border-radius:8px;
    font-weight:bold;
    margin-top:10px;
}}

.red{{
    background:#dc2626;
    color:white;
}}

.orange{{
    background:#f59e0b;
    color:white;
}}

.green{{
    background:#16a34a;
    color:white;
}}

.matched{{
    display:inline-block;
    background:#16a34a;
    color:white;
    padding:8px 12px;
    border-radius:8px;
    margin:5px;
}}

.missing{{
    display:inline-block;
    background:#dc2626;
    color:white;
    padding:8px 12px;
    border-radius:8px;
    margin:5px;
}}

</style>

</head>

<body>

<div class="card">

<h1>Candidate Report</h1>

<h2>{candidate[1]}</h2>

<div class="score">
{round(candidate[5],2)}%
</div>

<div class="section">
<h3>Email</h3>
<p>{candidate[2]}</p>
</div>

<div class="section">
<h3>Phone</h3>
<p>{candidate[3]}</p>
</div>

<div class="section">
<h3>Skills</h3>
{skills_html}
</div>

<div class="section">

<h3>Recommendation</h3>

<span class="recommendation {recommendation_class}">
    {recommendation}
</span>

</div>

<div class="section">

<h3>Matched Skills</h3>

{matched_html}

</div> 

<div class="section">

<h3>Missing Skills</h3>

{missing_html}

</div>

</div>

</body>

</html>
    """

    return HTMLResponse(content=html)

@app.post("/chat")
async def chat(request: ChatRequest):

    global chatbot_index
    global chatbot_chunks

    if chatbot_index is None:
        return {
            "error": "Upload a resume first"
        }

    answer = ask_resume_chatbot(
        request.message,
        chatbot_index,
        chatbot_chunks
    )

    print("CHATBOT ANSWER =", answer)
    print("CHATBOT ANSWER TYPE =", type(answer))

    return {
        "answer": answer
    }

@app.get("/debug")
def debug():

    cursor.execute(
        "SELECT * FROM candidates"
    )

    rows = cursor.fetchall()

    return {
        "data": rows
    }