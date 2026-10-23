import google.generativeai as genai
import os

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

    Return only a match score from 0 to 100.
    """

    response = model.generate_content(prompt)

    try:
        score = float(response.text.strip())
        return score
    except:
        return 50.0