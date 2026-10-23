import os
import google.generativeai as genai

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel("gemini-pro")


def get_ai_score(resume_text, jd_text):
    prompt = f"""
Compare this resume with the job description.

Resume:
{resume_text}

Job Description:
{jd_text}

Return only a numeric match score from 0 to 100.
"""

    try:
        response = model.generate_content(prompt)

        print("GEMINI RESPONSE =", response.text)

        score = float(response.text.strip())

        return score

    except Exception as e:

        print("Gemini Error =", e)

        return 50.0