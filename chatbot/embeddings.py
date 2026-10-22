from sentence_transformers import SentenceTransformer

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

def create_embeddings(texts):

    return embedding_model.encode(
        texts,
        convert_to_numpy=True
    )