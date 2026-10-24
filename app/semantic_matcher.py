import os
import re
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)



model = genai.GenerativeModel("models/gemini-3.5-flash-lite")


def get_ai_score(resume_text, jd_text):

    prompt = f"""
You are a Senior ATS Resume Evaluator.

Analyze this resume against this job description.

Job Description:
{jd_text}

Resume:
{resume_text}

Evaluate:

1. Skills Match
2. AI/ML Knowledge
3. Projects Relevance
4. Education Relevance
5. Experience Relevance

Give a realistic ATS score.

Scoring Guide:

90-100 = Excellent Match
70-89 = Strong Match
50-69 = Moderate Match
30-49 = Weak Match
0-29 = Poor Match

Return only one number between 0 and 100.

Examples:

85

72

91

Do not explain.
Do not give reasons.
Do not write percentage sign.
Only return the number.
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