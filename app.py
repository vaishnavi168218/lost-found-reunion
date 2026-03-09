"""
LOST & FOUND REUNION - Streamlit UI
Run: streamlit run app.py
"""

import streamlit as st
import os
from PIL import Image

# ─── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Lost & Found Reunion",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
    }
    .result-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
        background: #fafafa;
    }
    .confidence-high  { color: #2ecc71; font-weight: bold; }
    .confidence-med   { color: #f39c12; font-weight: bold; }
    .confidence-low   { color: #e74c3c; font-weight: bold; }
    .rank-badge {
        background: #667eea;
        color: white;
        border-radius: 50%;
        width: 32px;
        height: 32px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-weight: bold;
        margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ─── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔍 Lost & Found Reunion</h1>
    <p>Multi-Modal Semantic Search Engine · BLDEACET Campus</p>
</div>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Search Settings")
    top_k = st.slider("Number of results", 1, 10, 5)
    text_weight = st.slider("Text weight", 0.0, 1.0, 0.5, 0.1)
    img_weight  = 1.0 - text_weight
    st.write(f"Image weight: **{img_weight:.1f}**")

    st.divider()
    st.markdown("### 📖 How to use")
    st.markdown("""
    1. **Text search** — Describe your lost item in plain English
    2. **Image search** — Upload a photo of your lost item
    3. **Combined** — Use both for best results!
    4. Results ranked by **AI confidence score**
    5. Each match comes with an **AI explanation**
    """)

    st.divider()
    st.markdown("### 🏷️ Filter by category")
    try:
        import pandas as pd
        df = pd.read_csv("data/lost_found_dataset_cleaned.csv")
        categories = ["All"] + sorted(df["category"].unique().tolist())
        selected_cat = st.selectbox("Category", categories)
    except Exception:
        selected_cat = "All"

# ─── Search form ──────────────────────────────────────────────────────────────
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📝 Text Description")
    query_text = st.text_area(
        "Describe your lost item:",
        placeholder="e.g. gold AirPods Max headphones with leather case, lost in library",
        height=120,
    )

with col2:
    st.subheader("📷 Upload Image")
    uploaded_file = st.file_uploader(
        "Upload a photo of your lost item:",
        type=["jpg", "jpeg", "png", "webp"],
    )
    query_image = None
    if uploaded_file:
        query_image = Image.open(uploaded_file)
        st.image(query_image, caption="Your uploaded image", use_column_width=True)

# ─── Search button ────────────────────────────────────────────────────────────
search_clicked = st.button("🔍 Search Lost & Found", type="primary", use_container_width=True)

if search_clicked:
    if not query_text.strip() and query_image is None:
        st.warning("⚠️ Please enter a text description or upload an image.")
    else:
        with st.spinner("🔄 Searching with AI…"):
            try:
                from phase4_search_engine import search
                results = search(
                    query_text=query_text.strip(),
                    query_image=query_image,
                    top_k=top_k,
                    text_weight=text_weight,
                    img_weight=img_weight,
                )

                # Apply category filter
                if selected_cat != "All":
                    results = [r for r in results if r["category"] == selected_cat]

            except Exception as e:
                st.error(f"Search error: {e}")
                st.exception(e)
                results = []

        if not results:
            st.info("No results found. Try a different query or category filter.")
        else:
            st.success(f"✅ Found **{len(results)}** potential matches!")
            st.divider()

            for r in results:
                with st.container():
                    conf = r["confidence"]
                    conf_class = (
                        "confidence-high" if conf >= 0.7 else
                        "confidence-med"  if conf >= 0.4 else
                        "confidence-low"
                    )
                    conf_pct = f"{conf:.0%}"

                    img_col, info_col = st.columns([1, 3])

                    with img_col:
                        img_path = r.get("image_path", "")
                        if os.path.exists(img_path):
                            item_img = Image.open(img_path)
                            st.image(item_img, use_column_width=True)
                        else:
                            st.markdown("🖼️ *No image*")

                    with info_col:
                        st.markdown(
                            f"**#{r['rank']}  {r['product_name']}**  "
                            f"·  `{r['category']}`  "
                            f"·  <span class='{conf_class}'>Match: {conf_pct}</span>",
                            unsafe_allow_html=True,
                        )
                        st.progress(conf, text=f"Confidence: {conf_pct}")
                        st.markdown(f"📋 **Lost report:** {r['lost_item_description']}")
                        st.info(f"🤖 **AI says:** {r['explanation']}")

                    st.divider()

# ─── Stats section ─────────────────────────────────────────────────────────────
with st.expander("📊 Database Statistics"):
    try:
        import pandas as pd
        df = pd.read_csv("data/lost_found_dataset_cleaned.csv")
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Items", len(df))
        c2.metric("Categories", df["category"].nunique())
        c3.metric("Avg Price", f"₹{df['price'].mean():.0f}" if "price" in df else "—")
        st.bar_chart(df["category"].value_counts())
    except Exception as e:
        st.write(f"Stats unavailable: {e}")

# ─── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
---
<center>Built with ❤️ for BLDEACET · Progress Project 1 · 
Powered by CLIP + Sentence-Transformers + FAISS + Streamlit</center>
""", unsafe_allow_html=True)
