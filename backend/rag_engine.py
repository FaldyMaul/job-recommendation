# backend/rag_engine.py

import pandas as pd
from sentence_transformers import SentenceTransformer
from chromadb import PersistentClient

# Initialize embedding model
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# Setup Chroma persistent client
chroma_client = PersistentClient(path="db/vectorstore")
collection = chroma_client.get_or_create_collection(name="competencies")

def load_competency_data(csv_path="data/direktori_komp.csv"):
    """Load and clean the competency CSV."""
    df = pd.read_csv(csv_path, sep="|")
    df = df.dropna(subset=["Competency", "Definition"]).reset_index(drop=True)
    return df

def embed_competencies(df: pd.DataFrame):
    """Embed competencies into Chroma vectorstore."""
    descriptions = df["Definition"].astype(str).tolist()
    embeddings = embedding_model.encode(descriptions).tolist()
    ids = [f"comp_{i}" for i in range(len(df))]

    # Clear and re-add to avoid duplicates if needed
    collection.delete(ids=ids)
    collection.add(
        documents=descriptions,
        embeddings=embeddings,
        ids=ids,
        metadatas=df.to_dict(orient="records")
    )

def query_competency(text: str, top_k: int = 5):
    """Query top-k similar competencies for given text."""
    query_embedding = embedding_model.encode([text])[0]
    return collection.query(query_embeddings=[query_embedding], n_results=top_k)

def get_all_competency_names():
    """Return list of all competency names."""
    df = load_competency_data()
    return df["Competency"].dropna().unique().tolist()

def query_competency_by_name(name: str):
    """Fetch definition and metadata for a given competency name."""
    df = load_competency_data()
    row = df[df["Competency"].str.lower() == name.lower()]
    if not row.empty:
        row = row.iloc[0]
        return {
            "definition": row["Definition"],
            "metadata": row.to_dict()
        }
    return None
