from pathlib import Path

import pandas as pd
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"

cards = pd.read_csv(
    REFERENCE_DIR / "cards.csv"
)


errors = []


print(f"Prüfe {len(cards)} Karten ...")
print()


for _, card in cards.iterrows():

    image_path = IMAGE_DIR / card["image_file"]

    if not image_path.exists():

        errors.append(
            f"FEHLT: {image_path}"
        )

        continue

    try:
        with Image.open(image_path) as image:

            image.verify()

    except Exception as error:

        errors.append(
            f"DEFEKT: {image_path} - {error}"
        )


if errors:

    print("Es wurden Probleme gefunden:")
    print()

    for error in errors:
        print(error)

else:

    print("Alles OK.")
    print(
        f"{len(cards)} Kartenbilder "
        "wurden erfolgreich geprüft."
    )