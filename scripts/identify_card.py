import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embeddings import CardEmbedder


REFERENCE_DIR = ROOT / "data" / "reference"
EMBEDDING_DIR = ROOT / "data" / "embeddings"


def identify_card(image_path: Path, top_k: int = 5):
    embeddings = np.load(
        EMBEDDING_DIR / "embeddings.npy"
    )

    card_ids = np.load(
        EMBEDDING_DIR / "card_ids.npy"
    )

    cards = pd.read_csv(
        REFERENCE_DIR / "cards.csv"
    )

    embedder = CardEmbedder()

    query_embedding = embedder.get_embedding(
        image_path
    )

    # Da Referenzvektoren und Query normalisiert sind,
    # entspricht das Skalarprodukt der Cosine Similarity.
    similarities = embeddings @ query_embedding

    top_k = min(top_k, len(similarities))

    best_indices = np.argsort(
        similarities
    )[::-1][:top_k]

    print()
    print(f"Suchbild: {image_path}")
    print()
    print(f"TOP {top_k} TREFFER")
    print("-" * 75)

    for rank, index in enumerate(
        best_indices,
        start=1
    ):
        card_id = str(card_ids[index])

        card_match = cards[
            cards["card_id"].astype(str) == card_id
        ]

        if card_match.empty:
            print(
                f"{rank}. Unbekannte ID: {card_id}"
            )
            continue

        card = card_match.iloc[0]

        similarity = float(
            similarities[index]
        )

        print(
            f"{rank}. "
            f"{card['name']} | "
            f"{card['set_name']} | "
            f"{card['printed_number']} | "
            f"ID: {card_id} | "
            f"Similarity: {similarity:.4f}"
        )


def main():
    parser = argparse.ArgumentParser(
        description="Pokémon-Karte anhand ihres Bildes identifizieren."
    )

    parser.add_argument(
        "image",
        type=Path,
        help="Pfad zum zu erkennenden Kartenbild"
    )

    parser.add_argument(
        "--top-k",
        type=int,
        default=5,
        help="Anzahl der angezeigten Treffer"
    )

    args = parser.parse_args()

    identify_card(
        args.image,
        args.top_k
    )


if __name__ == "__main__":
    main()