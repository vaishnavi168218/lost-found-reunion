"""
PHASE 1: DATA SOURCING
Generates 150 realistic lost item entries using the Open Library / FakeStore API
and an LLM to create realistic lost item descriptions.
"""

import requests
import json
import csv
import os
import time
import random

# ─── CONFIG ──────────────────────────────────────────────────────────────────
OUTPUT_CSV = "data/scraped_products.csv"
IMAGES_DIR = "images"
os.makedirs("data", exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# ─── PRODUCT CATEGORIES (realistic lost items on a campus) ───────────────────
EXTRA_ITEMS = [
    # Electronics
    {"name": "Apple AirPods Pro", "category": "Electronics",
     "description": "Wireless noise-cancelling earbuds with charging case, white color",
     "price": 249.99,
     "image_url": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=400"},
    {"name": "Samsung Galaxy Watch", "category": "Electronics",
     "description": "Smartwatch with black silicone band, 44mm, GPS enabled",
     "price": 299.99,
     "image_url": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=400"},
    {"name": "Sony WH-1000XM5 Headphones", "category": "Electronics",
     "description": "Over-ear wireless headphones, black, with carrying case",
     "price": 349.99,
     "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400"},
    {"name": "iPad Mini", "category": "Electronics",
     "description": "Apple iPad Mini 6th gen, 64GB, space gray, with smart cover",
     "price": 499.99,
     "image_url": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=400"},
    {"name": "Logitech MX Master Mouse", "category": "Electronics",
     "description": "Wireless ergonomic mouse, dark gray, Bluetooth",
     "price": 99.99,
     "image_url": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400"},
    {"name": "HP Laptop Charger", "category": "Electronics",
     "description": "65W USB-C laptop charger, black cable, HP branded",
     "price": 45.99,
     "image_url": "https://images.unsplash.com/photo-1585771724684-38269d6639fd?w=400"},
    {"name": "Kindle Paperwhite", "category": "Electronics",
     "description": "Amazon Kindle e-reader, black, waterproof, 8GB",
     "price": 139.99,
     "image_url": "https://images.unsplash.com/photo-1510982096513-f4e28ce06df4?w=400"},
    {"name": "JBL Portable Speaker", "category": "Electronics",
     "description": "JBL Flip 6 Bluetooth speaker, teal/blue color, cylindrical",
     "price": 129.99,
     "image_url": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=400"},
    {"name": "iPhone 14 Case", "category": "Electronics",
     "description": "Clear MagSafe case for iPhone 14, with wallet attachment",
     "price": 39.99,
     "image_url": "https://images.unsplash.com/photo-1601784551446-20c9e07cdbdb?w=400"},
    {"name": "USB-C Hub", "category": "Electronics",
     "description": "7-in-1 USB-C hub, silver aluminum, multiple ports",
     "price": 49.99,
     "image_url": "https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=400"},

    # Bags & Accessories
    {"name": "Nike Backpack", "category": "Bags",
     "description": "Black Nike Brasilia backpack, medium size, with laptop compartment",
     "price": 55.00,
     "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"},
    {"name": "Leather Wallet", "category": "Accessories",
     "description": "Brown bifold leather wallet with card slots and cash compartment",
     "price": 35.00,
     "image_url": "https://images.unsplash.com/photo-1627123424574-724758594e93?w=400"},
    {"name": "Tote Bag", "category": "Bags",
     "description": "Canvas tote bag, navy blue, with university logo print",
     "price": 20.00,
     "image_url": "https://images.unsplash.com/photo-1584917865442-de89df76afd3?w=400"},
    {"name": "Hydro Flask Water Bottle", "category": "Accessories",
     "description": "32oz stainless steel water bottle, forest green, with straw lid",
     "price": 49.95,
     "image_url": "https://images.unsplash.com/photo-1602143407151-7111542de6e8?w=400"},
    {"name": "Sunglasses", "category": "Accessories",
     "description": "Ray-Ban Wayfarer sunglasses, black frame, polarized lenses",
     "price": 153.00,
     "image_url": "https://images.unsplash.com/photo-1511499767150-a48a237f0083?w=400"},
    {"name": "Umbrella", "category": "Accessories",
     "description": "Compact automatic umbrella, navy blue, with carrying sleeve",
     "price": 25.00,
     "image_url": "https://images.unsplash.com/photo-1520697830682-bbb6e85e2b0b?w=400"},
    {"name": "Gym Bag", "category": "Bags",
     "description": "Adidas duffel bag, black and white stripes, medium size",
     "price": 40.00,
     "image_url": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=400"},
    {"name": "Laptop Sleeve", "category": "Bags",
     "description": "13-inch neoprene laptop sleeve, gray, with accessories pocket",
     "price": 19.99,
     "image_url": "https://images.unsplash.com/photo-1625895197185-efcec01cffe0?w=400"},
    {"name": "Crossbody Bag", "category": "Bags",
     "description": "Small leather crossbody bag, tan/camel color, with gold hardware",
     "price": 65.00,
     "image_url": "https://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=400"},
    {"name": "Keychain", "category": "Accessories",
     "description": "Metal keychain with multiple keys and a small flashlight",
     "price": 12.00,
     "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400"},

    # Stationery & Books
    {"name": "Notebook Bundle", "category": "Stationery",
     "description": "Set of 3 Leuchtturm1917 notebooks, dotted grid, A5 size",
     "price": 45.00,
     "image_url": "https://images.unsplash.com/photo-1544816155-12df9643f363?w=400"},
    {"name": "Scientific Calculator", "category": "Stationery",
     "description": "Casio FX-991EX scientific calculator, black, with cover",
     "price": 21.99,
     "image_url": "https://images.unsplash.com/photo-1564939558297-fc396f18e5c7?w=400"},
    {"name": "Textbook", "category": "Books",
     "description": "Engineering Mathematics textbook, thick blue hardcover, 800 pages",
     "price": 89.00,
     "image_url": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400"},
    {"name": "Pen Set", "category": "Stationery",
     "description": "Pilot G2 pen set, assorted colors, pack of 12",
     "price": 14.99,
     "image_url": "https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400"},
    {"name": "Pencil Case", "category": "Stationery",
     "description": "Large canvas pencil case, floral pattern, full of art supplies",
     "price": 18.00,
     "image_url": "https://images.unsplash.com/photo-1588196749597-9ff075ee6b5b?w=400"},

    # Clothing
    {"name": "College Hoodie", "category": "Clothing",
     "description": "BLDEACET college hoodie, maroon color, size M, fleece lined",
     "price": 35.00,
     "image_url": "https://images.unsplash.com/photo-1556821840-3a63f15732ce?w=400"},
    {"name": "Denim Jacket", "category": "Clothing",
     "description": "Blue denim jacket, medium wash, size L, with pin badges",
     "price": 79.99,
     "image_url": "https://images.unsplash.com/photo-1576995853123-5a10305d93c0?w=400"},
    {"name": "Sports Cap", "category": "Clothing",
     "description": "Nike Dri-FIT cap, black, adjustable strap, curved brim",
     "price": 28.00,
     "image_url": "https://images.unsplash.com/photo-1588850561407-ed78c282e89b?w=400"},
    {"name": "Scarf", "category": "Clothing",
     "description": "Wool plaid scarf, red and black tartan pattern, long",
     "price": 22.00,
     "image_url": "https://images.unsplash.com/photo-1520903920243-00d872a2d1c9?w=400"},
    {"name": "Gloves", "category": "Clothing",
     "description": "Black leather touchscreen gloves, size M, lined interior",
     "price": 30.00,
     "image_url": "https://images.unsplash.com/photo-1584534735734-85f24218f5a9?w=400"},
]

# ─── LOST ITEM DESCRIPTION TEMPLATES ─────────────────────────────────────────
LOSS_CONTEXTS = [
    "I left it in the library on the second floor near the study tables.",
    "Forgot it in the canteen after lunch yesterday.",
    "Left it in Lecture Hall B during the afternoon session.",
    "I think I dropped it somewhere near the main entrance.",
    "Left it in the computer lab after practicals.",
    "Forgot it near the basketball court after evening sports.",
    "I left it in the hostel common room last night.",
    "Dropped it somewhere between the admin block and the cafeteria.",
    "Left it on the bench outside the mechanical department.",
    "Forgot it in the exam hall after the test.",
]

LOSS_DESCRIPTIONS = [
    "Please help me find it, it was a gift.",
    "I really need it for my studies.",
    "It has my notes inside it.",
    "It's very important to me.",
    "I've been looking for it everywhere.",
    "Reward if found!",
    "Please call me if you find it.",
    "It has my name written on it.",
]


def generate_lost_description(product_name, product_desc, category):
    """Generate a realistic student lost-item report."""
    context = random.choice(LOSS_CONTEXTS)
    note = random.choice(LOSS_DESCRIPTIONS)
    
    # Simplified description (like a real student would write)
    simple_words = {
        "Electronics": ["device", "gadget", "thing", "electronic item"],
        "Bags": ["bag", "backpack", "purse"],
        "Accessories": ["item", "accessory", "thing"],
        "Stationery": ["stationery item", "school supply"],
        "Books": ["book", "textbook"],
        "Clothing": ["clothing item", "garment"],
    }
    alt_word = random.choice(simple_words.get(category, ["item"]))

    return f"Lost my {product_name}. {context} {note} It is a {alt_word} - {product_desc[:80]}."


def fetch_fakestoreapi_products():
    """Fetch products from FakeStore API (free, no key needed)."""
    try:
        resp = requests.get("https://fakestoreapi.com/products", timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"FakeStore API error: {e}")
    return []


def build_dataset():
    products = []

    # Try FakeStore API first
    print("📦 Fetching from FakeStore API...")
    api_products = fetch_fakestoreapi_products()
    for p in api_products:
        products.append({
            "id": len(products) + 1,
            "name": p.get("title", "Unknown Item"),
            "category": p.get("category", "general").title(),
            "description": p.get("description", ""),
            "price": p.get("price", 0.0),
            "image_url": p.get("image", ""),
        })
    print(f"  ✅ Got {len(api_products)} products from FakeStore API")

    # Add our curated campus items
    for item in EXTRA_ITEMS:
        products.append({
            "id": len(products) + 1,
            **item
        })
    print(f"  ✅ Added {len(EXTRA_ITEMS)} curated campus items")

    # Generate lost item descriptions
    rows = []
    for p in products:
        lost_desc = generate_lost_description(p["name"], p["description"], p.get("category", "General"))
        rows.append({
            "id": p["id"],
            "product_name": p["name"],
            "category": p.get("category", "General"),
            "original_description": p["description"],
            "lost_item_description": lost_desc,
            "price": p.get("price", 0.0),
            "image_url": p.get("image_url", p.get("image", "")),
            "image_filename": f"item_{p['id']}.jpg",
        })

    # Save CSV
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n✅ Phase 1 Complete! Saved {len(rows)} items to {OUTPUT_CSV}")
    return rows


if __name__ == "__main__":
    print("=" * 60)
    print("PHASE 1: DATA SOURCING")
    print("=" * 60)
    data = build_dataset()
    print(f"\nSample entry:\n{json.dumps(data[0], indent=2)}")
