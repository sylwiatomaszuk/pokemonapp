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

QUERY_DIR = (
    ROOT /
    "data" /
    "queries" /
    "robust_evaluation"
)

QUERY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Für reproduzierbare Tests
RANDOM_SEED = 42

# Anzahl Testvarianten pro Karte
VARIANTS_PER_CARD = 5


def create_modified_image(
    image,
    rng
):
    height, width = image.shape[:2]

    modified = image.copy()

    # ----------------------------------------
    # 1. Zufällige Perspektivverzerrung
    # ----------------------------------------

    max_shift_x = int(width * 0.05)
    max_shift_y = int(height * 0.05)

    src = np.float32([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ])

    dst = np.float32([
        [
            rng.integers(0, max_shift_x + 1),
            rng.integers(0, max_shift_y + 1)
        ],
        [
            width - 1 - rng.integers(0, max_shift_x + 1),
            rng.integers(0, max_shift_y + 1)
        ],
        [
            width - 1 - rng.integers(0, max_shift_x + 1),
            height - 1 - rng.integers(0, max_shift_y + 1)
        ],
        [
            rng.integers(0, max_shift_x + 1),
            height - 1 - rng.integers(0, max_shift_y + 1)
        ],
    ])

    matrix = cv2.getPerspectiveTransform(
        src,
        dst
    )

    modified = cv2.warpPerspective(
        modified,
        matrix,
        (width, height),
        borderMode=cv2.BORDER_REPLICATE
    )

    # ----------------------------------------
    # 2. Leichte Rotation
    # ----------------------------------------

    angle = rng.uniform(
        -10,
        10
    )

    rotation_matrix = cv2.getRotationMatrix2D(
        (width / 2, height / 2),
        angle,
        1.0
    )

    modified = cv2.warpAffine(
        modified,
        rotation_matrix,
        (width, height),
        borderMode=cv2.BORDER_REPLICATE
    )

    # ----------------------------------------
    # 3. Helligkeit / Kontrast
    # ----------------------------------------

    alpha = rng.uniform(
        0.75,
        1.20
    )

    beta = rng.integers(
        -20,
        21
    )

    modified = cv2.convertScaleAbs(
        modified,
        alpha=alpha,
        beta=int(beta)
    )

    # ----------------------------------------
    # 4. Gelegentlich Blur
    # ----------------------------------------

    if rng.random() < 0.7:

        kernel = int(
            rng.choice([3, 5])
        )

        modified = cv2.GaussianBlur(
            modified,
            (kernel, kernel),
            0
        )

    # ----------------------------------------
    # 5. Leichtes Bildrauschen
    # ----------------------------------------

    noise_std = rng.uniform(
        0,
        6
    )

    noise = rng.normal(
        0,
        noise_std,
        modified.shape
    )

    modified = (
        modified.astype(np.float32)
        + noise
    )

    modified = np.clip(
        modified,
        0,
        255
    ).astype(np.uint8)

    return modified


def main():

    rng = np.random.default_rng(
        RANDOM_SEED
    )

    cards = pd.read_csv(
        REFERENCE_DIR / "cards.csv"
    )

    embeddings = np.load(
        EMBEDDING_DIR /
        "embeddings.npy"
    )

    card_ids = np.load(
        EMBEDDING_DIR /
        "card_ids.npy"
    ).astype(str)

    embedder = CardEmbedder()

    total_tests = (
        len(cards)
        * VARIANTS_PER_CARD
    )

    top1_correct = 0
    top3_correct = 0

    results = []

    print()
    print(
        f"Karten: {len(cards)}"
    )

    print(
        f"Varianten pro Karte: "
        f"{VARIANTS_PER_CARD}"
    )

    print(
        f"Tests insgesamt: "
        f"{total_tests}"
    )

    print()

    # ----------------------------------------
    # Alle Karten testen
    # ----------------------------------------

    for _, card in cards.iterrows():

        true_card_id = str(
            card["card_id"]
        )

        input_path = (
            IMAGE_DIR /
            card["image_file"]
        )

        original = cv2.imread(
            str(input_path)
        )

        if original is None:

            raise RuntimeError(
                f"Bild konnte nicht geladen "
                f"werden: {input_path}"
            )

        card_correct = 0

        for variant_index in range(
            VARIANTS_PER_CARD
        ):

            modified = create_modified_image(
                original,
                rng
            )

            query_path = (
                QUERY_DIR /
                f"{true_card_id}_"
                f"{variant_index}.jpg"
            )

            # Zufällige JPEG-Qualität
            jpeg_quality = int(
                rng.integers(
                    60,
                    96
                )
            )

            cv2.imwrite(
                str(query_path),
                modified,
                [
                    cv2.IMWRITE_JPEG_QUALITY,
                    jpeg_quality
                ]
            )

            query_embedding = (
                embedder.get_embedding(
                    query_path
                )
            )

            similarities = (
                embeddings
                @ query_embedding
            )

            ranking = np.argsort(
                similarities
            )[::-1]

            predicted_top1 = (
                card_ids[
                    ranking[0]
                ]
            )

            top3_ids = (
                card_ids[
                    ranking[:3]
                ]
            )

            best_similarity = float(
                similarities[
                    ranking[0]
                ]
            )

            second_similarity = float(
                similarities[
                    ranking[1]
                ]
            )

            similarity_margin = (
                best_similarity
                - second_similarity
            )

            is_top1 = (
                predicted_top1
                == true_card_id
            )

            is_top3 = (
                true_card_id
                in top3_ids
            )

            if is_top1:
                top1_correct += 1
                card_correct += 1

            if is_top3:
                top3_correct += 1

            results.append({
                "true_card_id":
                    true_card_id,

                "variant":
                    variant_index,

                "predicted_card_id":
                    predicted_top1,

                "top1_correct":
                    is_top1,

                "top3_correct":
                    is_top3,

                "best_similarity":
                    best_similarity,

                "second_similarity":
                    second_similarity,

                "margin":
                    similarity_margin
            })

        print(
            f"{true_card_id:12} | "
            f"{card_correct}/"
            f"{VARIANTS_PER_CARD}"
        )

    # ----------------------------------------
    # Ergebnisse
    # ----------------------------------------

    top1_accuracy = (
        top1_correct
        / total_tests
        * 100
    )

    top3_accuracy = (
        top3_correct
        / total_tests
        * 100
    )

    results_df = pd.DataFrame(
        results
    )

    print()
    print("=" * 55)
    print("ROBUSTE EVALUATION")
    print("=" * 55)

    print(
        f"Top-1: "
        f"{top1_correct}/"
        f"{total_tests} "
        f"= {top1_accuracy:.1f} %"
    )

    print(
        f"Top-3: "
        f"{top3_correct}/"
        f"{total_tests} "
        f"= {top3_accuracy:.1f} %"
    )

    print()

    print(
        "Durchschnittliche "
        "Best-Similarity:"
    )

    print(
        f"{results_df['best_similarity'].mean():.4f}"
    )

    print()

    print(
        "Durchschnittlicher Abstand "
        "zwischen Platz 1 und Platz 2:"
    )

    print(
        f"{results_df['margin'].mean():.4f}"
    )

    print()

    print(
        "Kleinster beobachteter Abstand:"
    )

    print(
        f"{results_df['margin'].min():.4f}"
    )

    # ----------------------------------------
    # CSV speichern
    # ----------------------------------------

    output_file = (
        ROOT /
        "data" /
        "queries" /
        "robust_evaluation_results.csv"
    )

    results_df.to_csv(
        output_file,
        index=False
    )

    print()
    print(
        "Ergebnisse gespeichert unter:"
    )

    print(output_file)


if __name__ == "__main__":
    main()