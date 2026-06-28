import faiss

index = faiss.read_index(
    "app/vectorstore/candidates.faiss"
)

print(
    "Vectors:",
    index.ntotal
)

print(
    "Dimensions:",
    index.d
)