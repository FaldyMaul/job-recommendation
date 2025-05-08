from sentence_transformers import SentenceTransformer
import pandas as pd
from chromadb import PersistentClient

from backend.load_competencies import load_competency_data

# Initialize embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Connect to persistent ChromaDB
chroma_client = PersistentClient(path="db/vectorstore")
collection = chroma_client.get_or_create_collection(name="competencies")

def build_vector_store():
    df = load_competency_data()
    
    # Ensure required columns exist
    if "definition" not in df.columns or "competency" not in df.columns:
        raise ValueError("CSV must contain 'competency' and 'definition' columns.")
    
    texts = df["definition"].astype(str).tolist()
    embeddings = model.encode(texts).tolist()
    
    ids = [f"comp_{i}" for i in range(len(df))]
    metadatas = df.to_dict(orient="records")

    # Clear previous embeddings if any
    collection.delete(where={})  # Optional: clear before adding

    # Add to Chroma
    collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)

    print("✅ Vector store successfully built and persisted.")
