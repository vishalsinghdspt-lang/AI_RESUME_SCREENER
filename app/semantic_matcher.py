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


def get_ai_score(resume_text, jd_text):

    prompt = f"""
You are an expert ATS system.

Compare the resume with the job description.

JOB DESCRIPTION:
{jd_text}

RESUME:
{resume_text}

Score based on:

- Skills Match (40%)
- Experience Relevance (25%)
- Project Relevance (15%)
- Education Relevance (10%)
- Keyword Match (10%)

Scoring Rules:

90-100 = Excellent Match
75-89 = Strong Match
60-74 = Moderate Match
40-59 = Weak Match
0-39 = Poor Match

Return ONLY one number between 0 and 100.

Examples:

85

72

91
"""

    try:

        response = model.generate_content(prompt)

        result = response.text.strip()

        print("========== GEMINI ==========")
        print(result)
        print("============================")

        match = re.search(
            r"(\d+(\.\d+)?)",
            result
        )

        if match:
            score = float(
                match.group(1)
            )
            return max(0, min(score, 100))

        return 0.0

    except Exception as e:

        print("Gemini Error:", e)

        return 50.0