import sys
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.embeddings import CardEmbedder


REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"

EMBEDDING_DIR = ROOT / "data" / "embeddings"

TEMP_DIR = ROOT / "data" / "queries" / "evaluation"
TEMP_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def modify_image(
    input_path: Path,
    output_path: Path
):
    image = cv2.imread(str(input_path))

    if image is None:
        raise RuntimeError(
            f"Bild konnte nicht geladen werden: "
            f"{input_path}"
        )

    height, width = image.shape[:2]

    margin_x = int(width * 0.04)
    margin_y = int(height * 0.04)

    src = np.float32([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ])

    dst = np.float32([
        [margin_x, margin_y],
        [width - margin_x, 0],
        [width - 1, height - margin_y],
        [0, height - 1],
    ])

    matrix = cv2.getPerspectiveTransform(
        src,
        dst
    )

    modified = cv2.warpPerspective(
        image,
        matrix,
        (width, height),
        borderMode=cv2.BORDER_REPLICATE
    )

    modified = cv2.convertScaleAbs(
        modified,
        alpha=0.92,
        beta=-8
    )

    modified = cv2.GaussianBlur(
        modified,
        (3, 3),
        0
    )

    cv2.imwrite(
        str(output_path),
        modified
    )


def main():
    cards = pd.read_csv(
        REFERENCE_DIR / "cards.csv"
    )

    embeddings = np.load(
        EMBEDDING_DIR / "embeddings.npy"
    )

    card_ids = np.load(
        EMBEDDING_DIR / "card_ids.npy"
    ).astype(str)

    embedder = CardEmbedder()

    top1_correct = 0
    top3_correct = 0

    results = []

    print()
    print(
        f"Teste {len(cards)} Karten ..."
    )
    print()

    for _, card in cards.iterrows():
        true_card_id = str(
            card["card_id"]
        )

        input_path = (
            IMAGE_DIR /
            card["image_file"]
        )

        query_path = (
            TEMP_DIR /
            f"{true_card_id}.jpg"
        )

        modify_image(
            input_path,
            query_path
        )

        query_embedding = (
            embedder.get_embedding(
                query_path
            )
        )

        similarities = (
            embeddings @ query_embedding
        )

        ranking = np.argsort(
            similarities
        )[::-1]

        predicted_top1 = (
            card_ids[ranking[0]]
        )

        top3_ids = (
            card_ids[ranking[:3]]
        )

        is_top1 = (
            predicted_top1 == true_card_id
        )

        is_top3 = (
            true_card_id in top3_ids
        )

        if is_top1:
            top1_correct += 1

        if is_top3:
            top3_correct += 1

        results.append({
            "true_card_id": true_card_id,
            "predicted_card_id": predicted_top1,
            "top1_correct": is_top1,
            "top3_correct": is_top3,
            "best_similarity": float(
                similarities[ranking[0]]
            )
        })

        status = (
            "OK"
            if is_top1
            else "FALSCH"
        )

        print(
            f"{status:6} | "
            f"{true_card_id:12} -> "
            f"{predicted_top1:12} | "
            f"{similarities[ranking[0]]:.4f}"
        )

    total = len(cards)

    top1_accuracy = (
        top1_correct / total * 100
    )

    top3_accuracy = (
        top3_correct / total * 100
    )

    print()
    print("=" * 50)
    print("ERGEBNIS")
    print("=" * 50)

    print(
        f"Top-1: "
        f"{top1_correct}/{total} "
        f"= {top1_accuracy:.1f} %"
    )

    print(
        f"Top-3: "
        f"{top3_correct}/{total} "
        f"= {top3_accuracy:.1f} %"
    )

    results_file = (
        ROOT /
        "data" /
        "queries" /
        "evaluation_results.csv"
    )

    pd.DataFrame(
        results
    ).to_csv(
        results_file,
        index=False
    )

    print()
    print(
        f"Ergebnisse gespeichert unter:"
    )
    print(results_file)


if __name__ == "__main__":
    main()