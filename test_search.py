from app.vectorstore.faiss_manager import (
    search
)

from app.services.embedding.bge_embedding import (
    createEmbedding
)

query = """
AI Engineer with Python,
FastAPI and LLM experience
"""

embedding = createEmbedding(
    query
)

results = search(
    embedding,
    k=5
)

print(results)