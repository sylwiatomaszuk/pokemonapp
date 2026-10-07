import sys
from pathlib import Path

import numpy as np
import pandas as pd
from tqdm import tqdm


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embeddings import CardEmbedder


REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"

OUTPUT_DIR = ROOT / "data" / "embeddings"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def main():
    cards_file = REFERENCE_DIR / "cards.csv"

    if not cards_file.exists():
        raise FileNotFoundError(
            f"cards.csv wurde nicht gefunden: {cards_file}"
        )

    cards = pd.read_csv(cards_file)

    print()
    print(f"{len(cards)} Referenzkarten gefunden.")
    print()

    embedder = CardEmbedder()

    embeddings = []
    card_ids = []

    for _, card in tqdm(
        cards.iterrows(),
        total=len(cards),
        desc="Embeddings erzeugen"
    ):
        image_path = IMAGE_DIR / card["image_file"]

        embedding = embedder.get_embedding(image_path)

        embeddings.append(embedding)
        card_ids.append(str(card["card_id"]))

    embeddings = np.stack(embeddings).astype(np.float32)

    np.save(
        OUTPUT_DIR / "embeddings.npy",
        embeddings
    )

    np.save(
        OUTPUT_DIR / "card_ids.npy",
        np.array(card_ids, dtype=str)
    )

    print()
    print("----------------------------------------")
    print("FERTIG")
    print("----------------------------------------")
    print(f"Karten:     {len(card_ids)}")
    print(f"Dimension:  {embeddings.shape}")
    print(
        f"Embeddings: "
        f"{OUTPUT_DIR / 'embeddings.npy'}"
    )


if __name__ == "__main__":
    main()