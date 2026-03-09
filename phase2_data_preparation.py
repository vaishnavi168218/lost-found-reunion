"""
PHASE 2: DATA PREPARATION
Cleans the scraped data, downloads images, standardizes categories,
removes duplicates, and creates combined searchable text fields.
"""

import pandas as pd
import requests
import os
import time
from pathlib import Path
from PIL import Image
from io import BytesIO

INPUT_CSV  = "data/scraped_products.csv"
OUTPUT_CSV = "data/lost_found_dataset_cleaned.csv"
IMAGES_DIR = "images"
os.makedirs(IMAGES_DIR, exist_ok=True)

# ─── CATEGORY STANDARDIZATION ─────────────────────────────────────────────────
CATEGORY_MAP = {
    "men's clothing":    "Clothing",
    "women's clothing":  "Clothing",
    "jewelery":          "Accessories",
    "electronics":       "Electronics",
    "general":           "General",
    "bags":              "Bags",
    "stationery":        "Stationery",
    "books":             "Books",
    "clothing":          "Clothing",
    "accessories":       "Accessories",
}

PLACEHOLDER_URL = "https://via.placeholder.com/400x400.png?text=No+Image"


def download_image(url: str, filepath: str) -> bool:
    """Download an image and save it locally. Returns True on success."""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        resp = requests.get(url, timeout=10, headers=headers)
        if resp.status_code == 200:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img = img.resize((224, 224))
            img.save(filepath, "JPEG", quality=85)
            return True
    except Exception as e:
        print(f"  ⚠️  Could not download {url[:60]}: {e}")
    return False


def clean_text(text: str) -> str:
    """Basic text cleaning."""
    if not isinstance(text, str):
        return ""
    return " ".join(text.strip().split())


def standardize_category(cat: str) -> str:
    return CATEGORY_MAP.get(str(cat).lower().strip(), "General")


def create_combined_text(row) -> str:
    """Merge all text fields into one searchable string."""
    parts = [
        str(row.get("product_name", "")),
        str(row.get("category", "")),
        str(row.get("original_description", "")),
        str(row.get("lost_item_description", "")),
    ]
    return " | ".join(p for p in parts if p)


def prepare_data():
    print("=" * 60)
    print("PHASE 2: DATA PREPARATION")
    print("=" * 60)

    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded {len(df)} rows from {INPUT_CSV}")

    # ── Clean text fields ──────────────────────────────────────────────────────
    df["product_name"]         = df["product_name"].apply(clean_text)
    df["original_description"] = df["original_description"].apply(clean_text)
    df["lost_item_description"]= df["lost_item_description"].apply(clean_text)

    # ── Standardize category ───────────────────────────────────────────────────
    df["category"] = df["category"].apply(standardize_category)

    # ── Remove duplicates ──────────────────────────────────────────────────────
    before = len(df)
    df.drop_duplicates(subset=["product_name"], inplace=True)
    df.reset_index(drop=True, inplace=True)
    df["id"] = df.index + 1
    print(f"Removed {before - len(df)} duplicate rows. {len(df)} remain.")

    # ── Download images ────────────────────────────────────────────────────────
    print("\n📸 Downloading images...")
    success = 0
    for _, row in df.iterrows():
        img_path = os.path.join(IMAGES_DIR, f"item_{row['id']}.jpg")
        df.at[row.name, "image_filename"] = f"item_{row['id']}.jpg"
        if os.path.exists(img_path):
            success += 1
            continue
        url = str(row.get("image_url", "")) or PLACEHOLDER_URL
        if download_image(url, img_path):
            success += 1
        else:
            # Save placeholder
            ph_img = Image.new("RGB", (224, 224), color=(200, 200, 200))
            ph_img.save(img_path)
        time.sleep(0.05)  # be polite
    print(f"  ✅ {success}/{len(df)} images ready")

    # ── Combined searchable text ───────────────────────────────────────────────
    df["combined_text"] = df.apply(create_combined_text, axis=1)

    # ── Save cleaned CSV ───────────────────────────────────────────────────────
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✅ Phase 2 Complete! Saved {len(df)} cleaned items → {OUTPUT_CSV}")

    # ── Quick stats ────────────────────────────────────────────────────────────
    print("\n📊 Category Distribution:")
    print(df["category"].value_counts().to_string())

    return df


if __name__ == "__main__":
    df = prepare_data()
    print(f"\nSample row:\n{df.iloc[0].to_dict()}")
