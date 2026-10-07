import csv
import json
import re
from pathlib import Path


DATASET_DIR = Path(r"C:\Users\sylwi\Documents\PokemonData\Pokemon TCG\Pokemon TCG")
SETS_FILE = Path("data/official_metadata/sets.json")
OUTPUT_FILE = Path("data/set_mapping.csv")


# Eindeutig aus den Dateinamen bzw. Ordnernamen ermittelte Sonder-Mappings.
MANUAL_MAPPINGS = {
    "base-set": "base1",
    "expedition": "ecard1",
    "champions-path": "swsh35",
    "pokemon-go": "pgo",
    "rumble": "ru1",

    "triumphant": "hgss4",
    "undaunted": "hgss3",
    "unleashed": "hgss2",

    "black-white-promos": "bwp",
    "diamond-pearl-promos": "dpp",
    "heartgold-soulsilver-promos": "hsp",
    "scarlet-violet-promos": "svp",
    "sword-shield-promos": "swshp",
    "xy-promos": "xyp",

    "pokemon-futsal-promos-2020": "fut20",

    "xy-trainer-kit-bisharp": "tk7a",
    "xy-trainer-kit-latias": "tk8b",
    "xy-trainer-kit-latios": "tk8a",
    "xy-trainer-kit-noivern": "tk6a",
    "xy-trainer-kit-pikachu-libre": "tk9a",
    "xy-trainer-kit-suicune": "tk9b",
    "xy-trainer-kit-sylveon": "tk6b",
    "xy-trainer-kit-wigglytuff": "tk7b",

    "black-white-trainer-kit-excadrill": "tk5b",
    "black-white-trainer-kit-zoroark": "tk5a",

    "diamond-pearl-trainer-kit-lucario": "tk3l",
    "diamond-pearl-trainer-kit-manaphy": "tk3a",

    "ex-trainer-kit-minun": "tk2m",
    "ex-trainer-kit-plusle": "tk2p",

    "hs-trainer-kit-gyarados": "tk4g",
    "hs-trainer-kit-raichu": "tk4r",

    "mcdonalds-collection-2011": "mcd11",
    "mcdonalds-collection-2012": "mcd12",
    "mcdonalds-collection-2016": "mcd16",
    "mcdonalds-collection-2019": "mcd19",
    "mcdonalds-collection-2021": "mcd21",
    "mcdonalds-collection-2022": "mcd22",

    "mega-evolution-promos": "me55",
        "black-white": "bw1",
    "diamond-pearl": "dp1",
    "firered-leafgreen": "ex6",
    "heartgold-soulsilver": "hgss1",
    "ruby-sapphire": "ex1",
    "scarlet-violet": "sv1",
    "sun-moon": "sm1",
    "sword-shield": "swsh1",
    "sun-moon-promos": "smp"
}


def normalize(value):
    value = value.lower().strip()
    value = value.replace("&", "and")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def load_official_sets():
    with SETS_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_official_lookup(sets):
    lookup = {}

    for s in sets:
        set_id = s.get("id", "")
        set_name = s.get("name", "")

        if set_id:
            lookup[normalize(set_id)] = s

        if set_name:
            lookup[normalize(set_name)] = s

    return lookup


def main():
    if not DATASET_DIR.exists():
        raise FileNotFoundError(f"Dataset nicht gefunden: {DATASET_DIR}")

    if not SETS_FILE.exists():
        raise FileNotFoundError(f"Official metadata nicht gefunden: {SETS_FILE}")

    official_sets = load_official_sets()
    official_lookup = build_official_lookup(official_sets)

    folders = sorted(
        p for p in DATASET_DIR.iterdir()
        if p.is_dir()
    )

    rows = []

    matched = 0
    no_match = 0
    manual = 0

    for folder in folders:
        source_folder = folder.name
        normalized_folder = normalize(source_folder)

        official_set = None
        mapping_type = "automatic"

        # 1. Manuelles Mapping prüfen
        if source_folder in MANUAL_MAPPINGS:
            official_id = MANUAL_MAPPINGS[source_folder]

            official_set = next(
                (
                    s for s in official_sets
                    if s.get("id") == official_id
                ),
                None
            )

            if official_set:
                mapping_type = "manual"
                manual += 1

        # 2. Automatisches Mapping
        if official_set is None:
            official_set = official_lookup.get(normalized_folder)

        if official_set:
            matched += 1

            rows.append({
                "source_folder": source_folder,
                "official_set_id": official_set.get("id", ""),
                "official_set_name": official_set.get("name", ""),
                "series": official_set.get("series", ""),
                "release_date": official_set.get("releaseDate", ""),
                "status": "matched",
                "mapping_type": mapping_type,
            })

        else:
            no_match += 1

            rows.append({
                "source_folder": source_folder,
                "official_set_id": "",
                "official_set_name": "",
                "series": "",
                "release_date": "",
                "status": "no_match",
                "mapping_type": "",
            })

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "source_folder",
                "official_set_id",
                "official_set_name",
                "series",
                "release_date",
                "status",
                "mapping_type",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print("=" * 60)
    print("SET MAPPING ERSTELLT")
    print("=" * 60)
    print(f"Dataset-Ordner:      {len(folders)}")
    print(f"Erfolgreich gemappt: {matched}")
    print(f"Davon manuell:       {manual}")
    print(f"Noch offen:          {no_match}")
    print()
    print(f"Gespeichert: {OUTPUT_FILE}")
    print()

    print("Noch offene Sets:")
    for row in rows:
        if row["status"] == "no_match":
            print(f"  - {row['source_folder']}")


if __name__ == "__main__":
    main()