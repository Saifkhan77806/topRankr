from app.services.embedding.bge_embedding import createEmbedding


def create_jd_embedding(summary):
    return createEmbedding(summary)