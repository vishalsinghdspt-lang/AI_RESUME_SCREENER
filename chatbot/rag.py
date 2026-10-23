from chatbot.gemini_client import model


def build_index(vectors):
    return vectors


def ask_resume_chatbot(question, index, chunks):

    resume_text = "\n".join(chunks)

    prompt = f"""
You are a resume assistant.

Answer ONLY from this resume.

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