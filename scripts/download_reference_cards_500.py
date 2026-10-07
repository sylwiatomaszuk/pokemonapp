from pathlib import Path
import csv
import requests
import numpy as np


ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"

REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


BASE_URL = (
    "https://raw.githubusercontent.com/"
    "PokemonTCG/pokemon-tcg-data/master"
)

SETS_URL = f"{BASE_URL}/sets/en.json"


TARGET_CARDS = 500
NUMBER_OF_PRIMARY_SETS = 20


def download_json(url):
    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    return response.json()


def download_image(url, output_path):
    response = requests.get(
        url,
        timeout=30
    )

    response.raise_for_status()

    output_path.write_bytes(
        response.content
    )


def get_pokemon_cards(set_id):

    cards_url = (
        f"{BASE_URL}/cards/en/"
        f"{set_id}.json"
    )

    try:
        cards = download_json(
            cards_url
        )

    except Exception as error:

        print(
            f"Set {set_id} "
            f"konnte nicht geladen werden:"
        )

        print(error)

        return []

    return [
        card
        for card in cards
        if card.get("supertype")
        == "Pokémon"
    ]


def main():

    print("Lade Set-Metadaten ...")

    all_sets = download_json(
        SETS_URL
    )

    # Nach Erscheinungsdatum sortieren
    all_sets = sorted(
        all_sets,
        key=lambda item:
            item.get(
                "releaseDate",
                "9999/99/99"
            )
    )

    print(
        f"{len(all_sets)} Sets gefunden."
    )

    # Sets gleichmäßig über die TCG-Geschichte auswählen
    indices = np.linspace(
        0,
        len(all_sets) - 1,
        NUMBER_OF_PRIMARY_SETS,
        dtype=int
    )

    primary_sets = [
        all_sets[index]
        for index in indices
    ]

    cards_per_set = (
        TARGET_CARDS
        // NUMBER_OF_PRIMARY_SETS
    )

    print()
    print(
        f"Ziel: {TARGET_CARDS} Karten"
    )

    print(
        f"Hauptsets: {NUMBER_OF_PRIMARY_SETS}"
    )

    print(
        f"ca. {cards_per_set} Karten pro Set"
    )

    print()

    csv_rows = []
    used_card_ids = set()
    used_set_ids = set()

    # Hauptsets
    for set_info in primary_sets:

        if len(csv_rows) >= TARGET_CARDS:
            break

        set_id = set_info["id"]
        set_name = set_info["name"]

        used_set_ids.add(set_id)

        printed_total = (
            set_info.get(
                "printedTotal",
                ""
            )
        )

        print()
        print("=" * 65)
        print(f"{set_name} ({set_id})")
        print("=" * 65)

        pokemon_cards = (
            get_pokemon_cards(
                set_id
            )
        )

        selected_cards = (
            pokemon_cards[
                :cards_per_set
            ]
        )

        for card in selected_cards:

            if len(csv_rows) >= TARGET_CARDS:
                break

            card_id = card["id"]

            if card_id in used_card_ids:
                continue

            used_card_ids.add(card_id)

            name = card["name"]
            number = card["number"]

            rarity = card.get(
                "rarity",
                ""
            )

            image_url = (
                card["images"]["large"]
            )

            image_file = (
                f"{card_id}.png"
            )

            image_path = (
                IMAGE_DIR /
                image_file
            )

            print(
                f"[{len(csv_rows)+1:03}/"
                f"{TARGET_CARDS}] "
                f"{name}"
            )

            if not image_path.exists():

                download_image(
                    image_url,
                    image_path
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

    # Falls die Hauptsets nicht auf 500 kommen:
    # mit weiteren Sets auffüllen
    if len(csv_rows) < TARGET_CARDS:

        print()
        print(
            "Fülle Datensatz mit "
            "weiteren Sets auf ..."
        )

        for set_info in all_sets:

            if len(csv_rows) >= TARGET_CARDS:
                break

            set_id = set_info["id"]

            if set_id in used_set_ids:
                continue

            used_set_ids.add(set_id)

            set_name = (
                set_info["name"]
            )

            printed_total = (
                set_info.get(
                    "printedTotal",
                    ""
                )
            )

            pokemon_cards = (
                get_pokemon_cards(
                    set_id
                )
            )

            for card in pokemon_cards:

                if len(csv_rows) >= TARGET_CARDS:
                    break

                card_id = (
                    card["id"]
                )

                if card_id in used_card_ids:
                    continue

                used_card_ids.add(
                    card_id
                )

                image_url = (
                    card["images"]["large"]
                )

                image_file = (
                    f"{card_id}.png"
                )

                image_path = (
                    IMAGE_DIR /
                    image_file
                )

                print(
                    f"[{len(csv_rows)+1:03}/"
                    f"{TARGET_CARDS}] "
                    f"{card['name']}"
                )

                if not image_path.exists():

                    download_image(
                        image_url,
                        image_path
                    )

                number = (
                    card["number"]
                )

                csv_rows.append({
                    "card_id": card_id,
                    "name": card["name"],
                    "set_id": set_id,
                    "set_name": set_name,
                    "number": number,
                    "printed_number":
                        f"{number}/{printed_total}",
                    "rarity":
                        card.get(
                            "rarity",
                            ""
                        ),
                    "image_file":
                        image_file,
                    "image_url":
                        image_url,
                })

    # CSV speichern
    csv_path = (
        REFERENCE_DIR /
        "cards.csv"
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
        writer.writerows(
            csv_rows
        )

    print()
    print("=" * 65)
    print("FERTIG")
    print("=" * 65)

    print(
        f"Karten: {len(csv_rows)}"
    )

    print(
        f"Verwendete Sets: "
        f"{len(used_set_ids)}"
    )

    print(
        f"CSV: {csv_path}"
    )


if __name__ == "__main__":
    main()