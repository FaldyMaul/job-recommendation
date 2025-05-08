from backend.rag_engine import load_competency_data, embed_competencies

df = load_competency_data("data/direktori_komp.csv")
embed_competencies(df)

print("✅ Competency data embedded successfully!")
