#!/usr/bin/env python3
"""
MASTER SETUP & RUN SCRIPT
Run this once to build the full pipeline end-to-end.
Usage:  python setup_and_run.py
"""

import subprocess
import sys
import os

def run(cmd, desc):
    print(f"\n{'='*60}")
    print(f"▶  {desc}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, shell=True)
    if result.returncode != 0:
        print(f"❌ Failed: {desc}")
        sys.exit(1)
    print(f"✅ Done: {desc}")


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    print("""
╔══════════════════════════════════════════════╗
║     LOST & FOUND REUNION - SETUP SCRIPT      ║
║     BLDEACET Progress Project 1              ║
╚══════════════════════════════════════════════╝
""")

    # 1. Install dependencies
    run(
        f"{sys.executable} -m pip install -q "
        "sentence-transformers transformers torch torchvision "
        "faiss-cpu pillow pandas requests streamlit "
        "openai-clip accelerate",
        "Installing Python dependencies"
    )

    # 2. Phase 1 - Data sourcing
    run(f"{sys.executable} phase1_data_sourcing.py", "Phase 1: Data Sourcing")

    # 3. Phase 2 - Data cleaning
    run(f"{sys.executable} phase2_data_preparation.py", "Phase 2: Data Preparation")

    # 4. Phase 3 - Embeddings
    run(f"{sys.executable} phase3_embeddings.py", "Phase 3: Embeddings + Vector Store")

    print("""
╔══════════════════════════════════════════════╗
║  ✅ SETUP COMPLETE! Launch the app with:     ║
║                                              ║
║    streamlit run app.py                      ║
║                                              ║
║  For ngrok tunnel (submission):              ║
║    ngrok http 8501                           ║
╚══════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
