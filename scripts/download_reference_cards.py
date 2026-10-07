from pathlib import Path
import csv
import requests


# --------------------------------------------------
# Projektpfade
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]

REFERENCE_DIR = ROOT / "data" / "reference"
IMAGE_DIR = REFERENCE_DIR / "images"

REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
IMAGE_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# Einstellungen
# --------------------------------------------------

SET_ID = "base1"
NUMBER_OF_CARDS = 20

CARDS_URL = (
    "https://raw.githubusercontent.com/"
    "PokemonTCG/pokemon-tcg-data/"
    f"master/cards/en/{SET_ID}.json"
)

SETS_URL = (
    "https://raw.githubusercontent.com/"
    "PokemonTCG/pokemon-tcg-data/"
    "master/sets/en.json"
)


def download_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    return response.json()


def download_image(url, output_path):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    output_path.write_bytes(response.content)


# --------------------------------------------------
# Set-Informationen laden
# --------------------------------------------------

print("Lade Set-Informationen ...")

sets = download_json(SETS_URL)

selected_set = next(
    (item for item in sets if item["id"] == SET_ID),
    None
)

if selected_set is None:
    raise RuntimeError(
        f"Set '{SET_ID}' wurde nicht gefunden."
    )

set_name = selected_set["name"]
printed_total = selected_set["printedTotal"]

print(f"Set: {set_name}")
print(f"Karten im Set: {printed_total}")


# --------------------------------------------------
# Kartendaten laden
# --------------------------------------------------

print()
print("Lade Kartendaten ...")

cards = download_json(CARDS_URL)


# Für den ersten Test wollen wir nur Pokémon-Karten.
pokemon_cards = [
    card
    for card in cards
    if card.get("supertype") == "Pokémon"
]

selected_cards = pokemon_cards[:NUMBER_OF_CARDS]


if len(selected_cards) < NUMBER_OF_CARDS:
    print(
        f"Achtung: Nur {len(selected_cards)} "
        "Pokémon-Karten gefunden."
    )


# --------------------------------------------------
# Bilder herunterladen
# --------------------------------------------------

csv_rows = []

print()
print("Lade Kartenbilder herunter ...")
print()


for index, card in enumerate(selected_cards, start=1):

    card_id = card["id"]
    name = card["name"]
    number = card["number"]
    rarity = card.get("rarity", "")

    image_url = card["images"]["large"]

    image_file = f"{card_id}.png"
    image_path = IMAGE_DIR / image_file

    print(
        f"[{index}/{len(selected_cards)}] "
        f"{name} ({card_id})"
    )

    if not image_path.exists():
        download_image(
            image_url,
            image_path
        )
    else:
        print("  → Bild bereits vorhanden")

    csv_rows.append(
        {
            "card_id": card_id,
            "name": name,
            "set_id": SET_ID,
            "set_name": set_name,
            "number": number,
            "printed_number": f"{number}/{printed_total}",
            "rarity": rarity,
            "image_file": image_file,
            "image_url": image_url,
        }
    )


# --------------------------------------------------
# CSV speichern
# --------------------------------------------------

csv_path = REFERENCE_DIR / "cards.csv"

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


print()
print("----------------------------------------")
print("FERTIG")
print("----------------------------------------")
print(
    f"{len(csv_rows)} Karten heruntergeladen."
)
print(f"Bilder: {IMAGE_DIR}")
print(f"CSV:    {csv_path}")