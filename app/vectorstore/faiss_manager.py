import faiss
import numpy as np
import pickle
import os


INDEX_FILE = (
    "app/vectorstore/"
    "candidates.faiss"
)

MAP_FILE = (
    "app/vectorstore/"
    "candidate_map.pkl"
)


if os.path.exists(INDEX_FILE):

    index = faiss.read_index(
        INDEX_FILE
    )

else:

    index = faiss.IndexFlatIP(
        384
    )


if os.path.exists(MAP_FILE):

    with open(
        MAP_FILE,
        "rb"
    ) as f:

        candidate_map = (
            pickle.load(f)
        )

else:

    candidate_map = {}


def add_candidate(
        candidate_id,
        embedding):

    global index
    global candidate_map

    vector = np.array(
        [embedding],
        dtype=np.float32
    )

    position = index.ntotal

    index.add(vector)

    candidate_map[
        position
    ] = candidate_id

    faiss.write_index(
        index,
        INDEX_FILE
    )

    with open(
        MAP_FILE,
        "wb"
    ) as f:

        pickle.dump(
            candidate_map,
            f
        )


def search(
        embedding,
        k=10):

    vector = np.array(
        [embedding],
        dtype=np.float32
    )

    scores, ids = (
        index.search(
            vector,
            k
        )
    )

    results = []

    for score, idx in zip(
            scores[0],
            ids[0]):

        if idx == -1:
            continue

        results.append({

            "candidate_id":
                candidate_map[idx],

            "score":
                float(score)
        })

    return results