from sentence_transformers import SentenceTransformer

embedding_model = None

def create_embeddings(texts):
    global embedding_model

    if embedding_model is None:
        embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

    return embedding_model.encode(
        texts,
        convert_to_numpy=True
    )