import email

from fastapi import FastAPI, UploadFile, File
from fastapi.responses import (
    HTMLResponse,
    FileResponse,
    RedirectResponse,
    JSONResponse
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

        cursor.execute(
            "SELECT last_insert_rowid()"
        )

        new_id = cursor.fetchone()[0]

        print("========== SAVED ==========")
        print("NAME =", name)
        print("ID =", new_id)
        print("SCORE =", ai_score)
        print("===========================")

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
    return FileResponse("templates/leaderboard.html")


@app.get("/candidate/{candidate_id}")
def candidate_report(candidate_id: int):
    return FileResponse("templates/candidate.html")


# Same reference list the old report page used (not the uploaded JD)
REFERENCE_SKILLS = [
    "Python",
    "React.js",
    "AWS",
    "Docker",
    "Kubernetes",
    "HTML",
    "CSS"
]


@app.get("/api/candidate/{candidate_id}")
def candidate_api(candidate_id: int):

    candidate = get_candidate(candidate_id)

    if candidate is None:
        return JSONResponse(
            {"error": "Candidate not found"},
            status_code=404
        )

    skills = [
        s.strip()
        for s in (candidate[4] or "").split(",")
        if s.strip()
    ]

    matched = [s for s in REFERENCE_SKILLS if s in skills]
    missing = [s for s in REFERENCE_SKILLS if s not in skills]

    score = candidate[5] or 0

    if score >= 80:
        recommendation = "Strong Match"
    elif score >= 50:
        recommendation = "Consider"
    else:
        recommendation = "Reject"

    return {
        "id": candidate[0],
        "name": candidate[1],
        "email": candidate[2],
        "phone": candidate[3],
        "skills": skills,
        "score": score,
        "recommendation": recommendation,
        "matched_skills": matched,
        "missing_skills": missing,
        "reference_skills": REFERENCE_SKILLS
    }

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

@app.get("/clear-database")
def clear_database():

    cursor.execute(
        "DELETE FROM candidates"
    )

    cursor.execute(
        "DELETE FROM sqlite_sequence WHERE name='candidates'"
    )

    conn.commit()

    return RedirectResponse(
        url="/",
        status_code=303
    )