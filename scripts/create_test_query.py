import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"
QUERY_DIR = ROOT / "data" / "queries"

QUERY_DIR.mkdir(
    parents=True,
    exist_ok=True
)


def create_query(card_id: str):
    cards = pd.read_csv(
        REFERENCE_DIR / "cards.csv"
    )

    card_match = cards[
        cards["card_id"].astype(str) == card_id
    ]

    if card_match.empty:
        raise ValueError(
            f"Karte mit ID '{card_id}' "
            "wurde nicht gefunden."
        )

    card = card_match.iloc[0]

    input_path = (
        IMAGE_DIR / card["image_file"]
    )

    image = cv2.imread(str(input_path))

    if image is None:
        raise RuntimeError(
            f"Bild konnte nicht geladen werden: "
            f"{input_path}"
        )

    height, width = image.shape[:2]

    # ------------------------------------------------
    # 1. leichte perspektivische Veränderung
    # ------------------------------------------------

    margin_x = int(width * 0.04)
    margin_y = int(height * 0.04)

    source_points = np.float32([
        [0, 0],
        [width - 1, 0],
        [width - 1, height - 1],
        [0, height - 1],
    ])

    destination_points = np.float32([
        [margin_x, margin_y],
        [width - margin_x, 0],
        [width - 1, height - margin_y],
        [0, height - 1],
    ])

    perspective_matrix = cv2.getPerspectiveTransform(
        source_points,
        destination_points
    )

    modified = cv2.warpPerspective(
        image,
        perspective_matrix,
        (width, height),
        borderMode=cv2.BORDER_REPLICATE
    )

    # ------------------------------------------------
    # 2. Helligkeit / Kontrast leicht verändern
    # ------------------------------------------------

    modified = cv2.convertScaleAbs(
        modified,
        alpha=0.92,
        beta=-8
    )

    # ------------------------------------------------
    # 3. leichte Unschärfe
    # ------------------------------------------------

    modified = cv2.GaussianBlur(
        modified,
        (3, 3),
        0
    )

    output_path = (
        QUERY_DIR /
        f"{card_id}_query.jpg"
    )

    success = cv2.imwrite(
        str(output_path),
        modified
    )

    if not success:
        raise RuntimeError(
            "Testbild konnte nicht gespeichert werden."
        )

    print()
    print("Testbild erstellt.")
    print(f"Karte:  {card['name']}")
    print(f"ID:     {card_id}")
    print(f"Datei:  {output_path}")


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "card_id",
        help="ID der Referenzkarte, z. B. base1-2"
    )

    args = parser.parse_args()

    create_query(args.card_id)


if __name__ == "__main__":
    main()