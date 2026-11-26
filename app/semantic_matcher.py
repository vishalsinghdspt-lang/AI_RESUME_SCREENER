import json
import os
import re
from unittest import result
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)



model = genai.GenerativeModel(
    "models/gemini-3.8-flash"
)


def analyze_resume(resume_text, jd_text):

    prompt = f"""
    You are an enterprise ATS system.

    Analyze the resume against the job description.

    JOB DESCRIPTION:
    {jd_text}

    RESUME:
    {resume_text}

    Return ONLY valid JSON.

    Format:

    {{
        "score": 0,
        "matched_skills": [],
        "missing_skills": [],
        "strengths": [],
        "weaknesses": [],
        "recommendation": ""
    }}

    Rules:

    1. Compare resume skills against JD skills.
    2. Consider experience relevance.
    3. Consider project relevance.
    4. Consider education relevance.
    5. Identify strengths.
    6. Identify weaknesses.
    7. Give recommendation.

    Recommendation must be:
    - Strong Match
    - Consider
    - Reject

    Return JSON only.
    """

    try:

        response = model.generate_content(prompt)

        result = response.text.strip()

        print("========== GEMINI ==========")
        print(result)
        print("============================")

        result = result.replace("```json", "")
        result = result.replace("```", "")

        analysis = json.loads(result)

        return analysis

    except Exception as e:

        print("Gemini Error:", e)

        return {
            "score": 0,
            "matched_skills": [],
            "missing_skills": [],
            "strengths": [],
            "weaknesses": [],
            "recommendation": "Reject"
        }