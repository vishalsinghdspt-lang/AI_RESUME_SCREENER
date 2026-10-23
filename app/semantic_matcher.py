import os
import re
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-1.5-flash")


def get_ai_score(resume_text, jd_text):

    prompt = f"""
Compare this resume with the job description.

Resume:
{resume_text}

Job Description:
{jd_text}

Return ONLY one number between 0 and 100.

Examples:

85

72

91

Do not write:
ATS Score
Percentage
%
Explanation
Any sentence

Return only a single numeric value.
"""

    try:

        response = model.generate_content(prompt)

        print("===================================")
        print("GEMINI RESPONSE =", response.text)
        print("===================================")

        numbers = re.findall(r"\d+", response.text)

        if numbers:
            score = float(numbers[0])

            if score > 100:
                score = 100

            if score < 0:
                score = 0

            return score

        return 50.0

    except Exception as e:

        print("Gemini Error =", e)

        return 0.0