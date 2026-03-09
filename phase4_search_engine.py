import os
import pickle
import requests
import numpy as np
import faiss
from PIL import Image
from sentence_transformers import SentenceTransformer

EMBEDDINGS_PKL  = "embeddings/lost_found_embeddings.pkl"
FAISS_INDEX_BIN = "embeddings/faiss_index.bin"
IMAGES_DIR      = "images"
TOP_K           = 5
OLLAMA_URL      = "http://localhost:11434/api/generate"
OLLAMA_MODEL    = "mistral"

_store       = None
_faiss_index = None
_text_model  = None


def _load_resources():
    global _store, _faiss_index, _text_model
    if _store is not None:
        return
    print("Loading embeddings & models...")
    with open(EMBEDDINGS_PKL, "rb") as f:
        _store = pickle.load(f)
    _faiss_index = faiss.read_index(FAISS_INDEX_BIN)
    _text_model  = SentenceTransformer(_store["text_model"])
    print("Resources loaded.")


def _norm(v):
    return v / (np.linalg.norm(v) + 1e-9)


def embed_query_text(text):
    emb = _text_model.encode([text], convert_to_numpy=True).squeeze()
    return _norm(emb).astype(np.float32)


def _llm_explain(query_text, item_name, item_desc, confidence):
    prompt = (
        f"A student lost: '{query_text}'.\n"
        f"Potential match: '{item_name}' — {item_desc[:120]}.\n"
        f"Confidence: {confidence:.0%}.\n"
        f"In 2 sentences explain why this could match and what to check."
    )
    try:
        resp = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=10,
        )
        if resp.status_code == 200:
            return resp.json().get("response", "").strip()
    except Exception:
        pass
    return (
        f"This item matches your description with {confidence:.0%} confidence. "
        f"Visit the Lost & Found office to check if '{item_name}' belongs to you "
        f"by verifying color, brand, and any personal markings."
    )


def search(query_text="", query_image=None, top_k=TOP_K,
           text_weight=0.5, img_weight=0.5):
    _load_resources()

    if not query_text and query_image is None:
        raise ValueError("Provide at least a text query or an image.")

    # Text-only mode
    q_emb = embed_query_text(query_text if query_text else "lost item")
    q_vec = q_emb[np.newaxis, :]

    scores, indices = _faiss_index.search(q_vec, top_k)
    scores  = scores[0]
    indices = indices[0]

    df = _store["df"]
    results = []
    for rank, (idx, score) in enumerate(zip(indices, scores), start=1):
        if idx < 0 or idx >= len(df):
            continue
        row = df.iloc[idx]
        confidence = float(np.clip(score, 0.0, 1.0))
        explanation = _llm_explain(
            query_text or "(image query)",
            str(row["product_name"]),
            str(row["lost_item_description"]),
            confidence,
        )
        results.append({
            "rank":                  rank,
            "id":                    int(row["id"]),
            "product_name":          str(row["product_name"]),
            "category":              str(row["category"]),
            "lost_item_description": str(row["lost_item_description"]),
            "image_filename":        str(row["image_filename"]),
            "image_path":            os.path.join(IMAGES_DIR, str(row["image_filename"])),
            "confidence":            confidence,
            "explanation":           explanation,
        })
    return results


if __name__ == "__main__":
    q = input("Enter search query: ").strip() or "wireless headphones"
    hits = search(query_text=q, top_k=5)
    for h in hits:
        print(f"\n#{h['rank']} [{h['confidence']:.0%}] {h['product_name']}")
        print(f"  {h['explanation']}")