from chatbot.gemini_client import model


def build_index(vectors):
    return vectors


def ask_resume_chatbot(question, index, chunks):

    resume_text = "\n".join(chunks)

    prompt = f"""
You are a professional ATS Resume Assistant.

Use only the information present in the resume.

Rules:
1. Answer only from the resume.
2. Do not use markdown.
3. Do not use * symbols.
4. Do not use ** symbols.
5. Use proper sentences.
6. If information is not present, say:
   "Information not found in the resume."

Resume:
{resume_text}

Question:
{question}
"""


    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"