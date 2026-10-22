from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def get_ai_score(resume_text, jd_text):

    resume_embedding = model.encode(resume_text)
    jd_embedding = model.encode(jd_text)

    similarity = cosine_similarity(
        [resume_embedding],
        [jd_embedding]
    )[0][0]

    return float(
    round(similarity * 100, 2)
)