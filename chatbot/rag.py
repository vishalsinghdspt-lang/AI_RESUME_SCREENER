import faiss
import numpy as np

def chunk_text(text):

    chunk_size = 500

    chunks = []

    for i in range(
        0,
        len(text),
        chunk_size
    ):

        chunks.append(
            text[i:i+chunk_size]
        )

    return chunks


def build_index(vectors):

    dimension = vectors.shape[1]

    index = faiss.IndexFlatL2(
        dimension
    )

    index.add(vectors)

    return index


def search_chunks(
    question_vector,
    index,
    chunks,
    k=5
):

    distances, indices = index.search(
        question_vector,
        k
    )

    return [
        chunks[i]
        for i in indices[0]
    ]

from chatbot.embeddings import create_embeddings
from chatbot.prompts import build_prompt
from chatbot.gemini_client import model


def ask_resume_chatbot(question, index, chunks):

    question_vector = create_embeddings(
        [question]
    )

    relevant_chunks = search_chunks(
        question_vector,
        index,
        chunks
    )

    context = "\n\n".join(
    relevant_chunks
    )

    candidate_name = "Candidate"

    score = 0

    retrieved_chunks = context

    job_description = "Not available"

    prompt = build_prompt(
        question,
        candidate_name,
        score,
        retrieved_chunks,
        job_description
    )

    response = model.generate_content(
        prompt
    )

    return response.text