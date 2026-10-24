import os
import re
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)



model = genai.GenerativeModel("models/gemini-3.5-flash-lite")


def get_ai_score(resume_text, jd_text):

    prompt = f"""
You are an ATS evaluator.

Evaluate the candidate against the job description.

Scoring:

Skills Match = 40 points
Experience Match = 25 points
Projects Match = 15 points
Education Match = 10 points
Technology Match = 10 points

Resume:
{resume_text}

Job Description:
{jd_text}

Return ONLY one number between 0 and 100.
"""

    try:

        response = model.generate_content(prompt)

        result = response.text.strip()

        print("Gemini Response:", result)

        match = re.search(r"\d+", result)

        if match:
            score = float(match.group())
            return max(0, min(score, 100))

        return 0.0

    except Exception as e:
        print("Gemini Error:", e)
        return 0.0