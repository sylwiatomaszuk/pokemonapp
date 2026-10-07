from pathlib import Path
import csv
import requests


ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"

REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 5 Sets × 20 Pokémon-Karten
# --------------------------------------------------

SETS_TO_DOWNLOAD = {
    "base1": 20,
    "neo1": 20,
    "ex1": 20,
    "swsh1": 20,
    "sv1": 20,
}


BASE_URL = (
    "https://raw.githubusercontent.com/"
    "PokemonTCG/pokemon-tcg-data/master"
)

SETS_URL = f"{BASE_URL}/sets/en.json"


def download_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


def download_image(url, output_path):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    output_path.write_bytes(response.content)


def main():

    print("Lade Set-Metadaten ...")

    all_sets = download_json(SETS_URL)

    sets_by_id = {
        item["id"]: item
        for item in all_sets
    }

    csv_rows = []

    print()

    for set_id, number_of_cards in SETS_TO_DOWNLOAD.items():

        if set_id not in sets_by_id:
            raise RuntimeError(
                f"Set '{set_id}' wurde nicht gefunden."
            )

        set_info = sets_by_id[set_id]

        set_name = set_info["name"]
        printed_total = set_info["printedTotal"]

        cards_url = (
            f"{BASE_URL}/cards/en/{set_id}.json"
        )

        print("=" * 60)
        print(f"Set: {set_name} ({set_id})")
        print("=" * 60)

        cards = download_json(cards_url)

        # Nur Pokémon-Karten
        pokemon_cards = [
            card
            for card in cards
            if card.get("supertype") == "Pokémon"
        ]

        selected_cards = pokemon_cards[
            :number_of_cards
        ]

        if len(selected_cards) < number_of_cards:
            print(
                f"Achtung: Nur "
                f"{len(selected_cards)} "
                f"Pokémon-Karten vorhanden."
            )

        for index, card in enumerate(
            selected_cards,
            start=1
        ):

            card_id = card["id"]
            name = card["name"]
            number = card["number"]
            rarity = card.get("rarity", "")

            image_url = card["images"]["large"]

            image_file = f"{card_id}.png"
            image_path = (
                IMAGE_DIR / image_file
            )

            print(
                f"[{index:02}/"
                f"{len(selected_cards):02}] "
                f"{name} ({card_id})"
            )

            if not image_path.exists():
                download_image(
                    image_url,
                    image_path
                )
            else:
                print(
                    "     Bild bereits vorhanden"
                )

            csv_rows.append({
                "card_id": card_id,
                "name": name,
                "set_id": set_id,
                "set_name": set_name,
                "number": number,
                "printed_number":
                    f"{number}/{printed_total}",
                "rarity": rarity,
                "image_file": image_file,
                "image_url": image_url,
            })

        print()

    # --------------------------------------------------
    # IDs auf Eindeutigkeit prüfen
    # --------------------------------------------------

    ids = [
        row["card_id"]
        for row in csv_rows
    ]

    if len(ids) != len(set(ids)):
        raise RuntimeError(
            "Doppelte card_id gefunden."
        )

    # --------------------------------------------------
    # CSV schreiben
    # --------------------------------------------------

    csv_path = (
        REFERENCE_DIR / "cards.csv"
    )

    fieldnames = [
        "card_id",
        "name",
        "set_id",
        "set_name",
        "number",
        "printed_number",
        "rarity",
        "image_file",
        "image_url",
    ]

    with csv_path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as csv_file:

        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(csv_rows)

    print("=" * 60)
    print("FERTIG")
    print("=" * 60)
    print(
        f"{len(csv_rows)} Karten "
        f"in cards.csv."
    )
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()