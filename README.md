# 🔍 Lost & Found Reunion
### BLDEACET Progress Project 1 — Multi-Modal Semantic Search Engine

---

## 🗂️ Project Structure

```
lost_found/
│
├── phase1_data_sourcing.py      # Scrapes/generates 150+ product entries
├── phase2_data_preparation.py   # Cleans data, downloads images
├── phase3_embeddings.py         # Generates text + image embeddings, builds FAISS index
├── phase4_search_engine.py      # Core search logic + LLM explanations
├── app.py                       # Streamlit web UI
├── setup_and_run.py             # One-click full pipeline runner
├── requirements.txt
│
├── data/
│   ├── scraped_products.csv         ← Phase 1 output
│   └── lost_found_dataset_cleaned.csv  ← Phase 2 output
│
├── images/
│   └── item_1.jpg ... item_N.jpg    ← Downloaded product images
│
└── embeddings/
    ├── lost_found_embeddings.pkl    ← Phase 3 output
    └── faiss_index.bin              ← FAISS vector index
```

---

## ⚡ Quick Start (Step by Step)

### Step 1 — Prerequisites
```bash
# Make sure you have Python 3.11+
python --version

# (Optional) Create a virtual environment
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows
```

### Step 2 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 3 — Run Phase 1: Data Sourcing
```bash
python phase1_data_sourcing.py
```
**What it does:**
- Fetches ~20 products from FakeStore API (free, no key needed)
- Adds 30 curated campus-realistic items (AirPods, calculators, hoodies, etc.)
- Uses templates to generate realistic lost-item reports for each
- Output: `data/scraped_products.csv`

### Step 4 — Run Phase 2: Data Preparation
```bash
python phase2_data_preparation.py
```
**What it does:**
- Cleans and standardizes all text fields
- Standardizes category names
- Downloads & resizes product images to `images/`
- Creates a `combined_text` field for richer search
- Output: `data/lost_found_dataset_cleaned.csv`

### Step 5 — Run Phase 3: Embeddings
```bash
python phase3_embeddings.py
```
**What it does:**
- Loads **Sentence-Transformers** (`all-MiniLM-L6-v2`) for 384-dim text embeddings
- Loads **CLIP** (`openai/clip-vit-base-patch32`) for 512-dim image embeddings
- Concatenates them into combined embeddings
- Stores in a **FAISS** inner-product index (cosine similarity)
- Output: `embeddings/lost_found_embeddings.pkl` + `embeddings/faiss_index.bin`

> ⏱️ First run downloads ~500MB of model weights. Subsequent runs are instant.

### Step 6 — Launch the App
```bash
streamlit run app.py
```
Open [http://localhost:8501](http://localhost:8501) in your browser.

---

## 🌐 Expose via ngrok (for submission)

```bash
# Install ngrok from https://ngrok.com/download
# Then in a new terminal while streamlit is running:
ngrok http 8501
```
Share the `https://xxxx.ngrok.io` URL with your professor.

---

## 🤖 Optional: Enable LLM Explanations (Ollama)

```bash
# Install Ollama: https://ollama.ai
ollama pull mistral
ollama serve
# Now the app will use Mistral to explain each match
```
Without Ollama, the app uses a built-in template-based explanation — still works!

---

## 🧠 How the Search Works

```
Student Query (text + optional image)
            │
            ▼
    ┌───────────────────────────────────┐
    │  Text Embedding (MiniLM, 384-dim) │
    │  Image Embedding (CLIP, 512-dim)  │
    └───────────────────────────────────┘
            │  Weighted concat + L2 norm
            ▼
    ┌───────────────────────────────────┐
    │   FAISS Inner Product Search      │
    │   (Cosine Similarity on normed    │
    │    combined vectors)              │
    └───────────────────────────────────┘
            │  Top-K results
            ▼
    ┌───────────────────────────────────┐
    │   Ollama LLM Explanation          │
    │   (or template fallback)          │
    └───────────────────────────────────┘
            │
            ▼
    Ranked results with confidence % + story
```

---

## 📊 Dataset Summary

| Field | Description |
|-------|-------------|
| `id` | Unique item ID |
| `product_name` | Real product name |
| `category` | Standardized: Electronics, Bags, Clothing… |
| `original_description` | Full product description |
| `lost_item_description` | AI-generated realistic student report |
| `image_filename` | Local image path |
| `combined_text` | Merged searchable text |

---

## 🔮 How I Would Improve It (Given More Time)

1. **Real scraping** — Scrape Flipkart/Amazon with Selenium for 500+ items
2. **Finer embeddings** — Fine-tune CLIP on campus-specific lost-item pairs
3. **User uploads** — Let students upload photos of found items to the DB
4. **GPS tagging** — Record where items were found on campus map
5. **Email alerts** — Notify student when a potential match is found
6. **Re-ranking** — Use a cross-encoder model for more accurate top-5
7. **Auth** — Student login via college ID to manage reports
8. **Admin dashboard** — Stats, bulk item management, donation scheduling

---

## 🛠️ Tools Used

| Tool | Purpose |
|------|---------|
| `sentence-transformers` | Text semantic embeddings |
| `transformers` + CLIP | Image embeddings |
| `FAISS` | Fast approximate nearest-neighbor search |
| `Ollama` (optional) | Local LLM for match explanations |
| `pandas` | Data cleaning |
| `Pillow` | Image processing |
| `Streamlit` | Web UI |
| `FakeStore API` | Free product data source |
| `ngrok` | Public tunnel for submission |

---

*Built for BLDEACET Progress Project 1 · Lost & Found Reunion*
