import os
import pickle
import numpy as np
import pandas as pd
import faiss
from sentence_transformers import SentenceTransformer

CLEANED_CSV   = "data/lost_found_dataset_cleaned.csv"
OUTPUT_PKL    = "embeddings/lost_found_embeddings.pkl"
OUTPUT_FAISS  = "embeddings/faiss_index.bin"
os.makedirs("embeddings", exist_ok=True)

TEXT_MODEL_NAME = "all-MiniLM-L6-v2"

def embed_text_batch(texts, model):
    embs = model.encode(texts, batch_size=64, show_progress_bar=True,
                        convert_to_numpy=True)
    norms = np.linalg.norm(embs, axis=1, keepdims=True) + 1e-9
    return (embs / norms).astype(np.float32)

def build_faiss_index(embeddings):
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)
    return index

def run_phase3():
    print("=" * 60)
    print("PHASE 3: EMBEDDINGS + VECTOR STORE (Text-Only Mode)")
    print("=" * 60)

    df = pd.read_csv(CLEANED_CSV)
    print(f"Loaded {len(df)} items")

    print("\n🔤 Loading sentence-transformer model...")
    model = SentenceTransformer(TEXT_MODEL_NAME)

    texts = df["combined_text"].fillna("").tolist()
    print("Encoding text...")
    text_embs = embed_text_batch(texts, model)
    print(f"  Text embeddings shape: {text_embs.shape}")

    img_embs = np.zeros((len(df), 512), dtype=np.float32)
    combined_embs = text_embs.copy()

    print("\n📦 Building FAISS index...")
    index = build_faiss_index(combined_embs)
    faiss.write_index(index, OUTPUT_FAISS)
    print(f"  FAISS index saved → {OUTPUT_FAISS}")

    store = {
        "df":            df,
        "text_embs":     text_embs,
        "img_embs":      img_embs,
        "combined_embs": combined_embs,
        "text_model":    TEXT_MODEL_NAME,
        "clip_model":    None,
        "mode":          "text_only",
    }
    with open(OUTPUT_PKL, "wb") as f:
        pickle.dump(store, f)
    print(f"  Embeddings saved → {OUTPUT_PKL}")
    print("\n✅ Phase 3 Complete! (Text-only mode)")
    return store

if __name__ == "__main__":
    run_phase3()