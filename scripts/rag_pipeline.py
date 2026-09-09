import os
import json
import numpy as np

from sentence_transformers import SentenceTransformer
import faiss


# -----------------------------
# PATHS
# -----------------------------

DATA_DIR = "data/bis/processed"
INDEX_DIR = "data/bis/index"

EMBEDDING_FILE = os.path.join(
    INDEX_DIR,
    "embeddings.npy"
)

METADATA_FILE = os.path.join(
    INDEX_DIR,
    "metadata.json"
)

FAISS_FILE = os.path.join(
    INDEX_DIR,
    "bis.index"
)


# -----------------------------
# SETTINGS
# -----------------------------

CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150

MODEL_NAME = "all-MiniLM-L6-v2"


# -----------------------------
# CHUNKING
# -----------------------------

def create_chunks(text):

    chunks = []

    start = 0

    while start < len(text):

        end = start + CHUNK_SIZE

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks


# -----------------------------
# LOAD BIS DOCUMENTS
# -----------------------------

def load_documents():

    documents = []

    for filename in os.listdir(DATA_DIR):

        if not filename.lower().endswith(".txt"):
            continue

        filepath = os.path.join(
            DATA_DIR,
            filename
        )

        print(f"Reading: {filename}")

        with open(
            filepath,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as f:

            text = f.read()

        chunks = create_chunks(text)

        for i, chunk in enumerate(chunks):

            documents.append({

                "text": chunk,

                "source": filename,

                "chunk_id": i

            })

    return documents


# -----------------------------
# CREATE VECTOR INDEX
# -----------------------------

def build_index():

    print()
    print("Loading BIS documents...")

    documents = load_documents()

    print()
    print(f"Total chunks: {len(documents)}")

    if len(documents) == 0:

        print("ERROR: No TXT files found.")

        return

    texts = [
        document["text"]
        for document in documents
    ]

    print()
    print("Loading embedding model...")

    model = SentenceTransformer(
        MODEL_NAME
    )

    print()
    print("Creating embeddings...")

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    embeddings = np.asarray(
        embeddings,
        dtype="float32"
    )

    os.makedirs(
        INDEX_DIR,
        exist_ok=True
    )

    # Save embeddings

    np.save(
        EMBEDDING_FILE,
        embeddings
    )

    # Save metadata

    with open(
        METADATA_FILE,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            documents,
            f,
            ensure_ascii=False,
            indent=2
        )

    # Create FAISS index

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(
        dimension
    )

    index.add(
        embeddings
    )

    faiss.write_index(
        index,
        FAISS_FILE
    )

    print()
    print("==============================")
    print("RAG INDEX CREATED SUCCESSFULLY")
    print("==============================")

    print(
        f"Documents/chunks: {len(documents)}"
    )

    print(
        f"Embedding dimension: {dimension}"
    )

    print(
        f"Index saved: {FAISS_FILE}"
    )


# -----------------------------
# SEARCH
# -----------------------------

def search(query, top_k=5):

    model = SentenceTransformer(
        MODEL_NAME
    )

    index = faiss.read_index(
        FAISS_FILE
    )

    with open(
        METADATA_FILE,
        "r",
        encoding="utf-8"
    ) as f:

        metadata = json.load(f)

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    query_embedding = np.asarray(
        query_embedding,
        dtype="float32"
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_number in zip(
        scores[0],
        indices[0]
    ):

        if index_number == -1:
            continue

        result = metadata[index_number].copy()

        result["score"] = float(score)

        results.append(result)

    return results


# -----------------------------
# TEST
# -----------------------------

if __name__ == "__main__":

    build_index()

    print()
    print("Testing RAG retrieval...")
    print()

    question = input(
        "Enter your BIS question: "
    )

    results = search(
        question,
        top_k=5
    )

    print()
    print("TOP RESULTS")
    print("==============================")

    for i, result in enumerate(
        results,
        start=1
    ):

        print()
        print(f"Result {i}")

        print(
            "Score:",
            result["score"]
        )

        print(
            "Source:",
            result["source"]
        )

        print(
            "Chunk:",
            result["chunk_id"]
        )

        print()
        print(
            result["text"][:700]
        )

        print(
            "------------------------------"
        )