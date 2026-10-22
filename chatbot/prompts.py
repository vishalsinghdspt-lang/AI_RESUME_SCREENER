def build_prompt(
    question,
    candidate_name,
    score,
    retrieved_chunks,
    job_description
):

    return f"""
You are a Senior Technical Recruiter.

Candidate Name:
{candidate_name}

Candidate Match Score:
{score}

Relevant Resume Information:
{retrieved_chunks}

Job Description:
{job_description}

Recruiter Question:
{question}

Instructions:

1. Answer the recruiter question.
2. Mention strengths.
3. Mention weaknesses.
4. Compare with job requirements.
5. Give hiring recommendation.
6. Be concise and professional.

"""