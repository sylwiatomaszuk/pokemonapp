from __future__ import annotations

import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


# Alle Pfade werden relativ zum Projektordner aufgelöst. Das Skript kann
# dadurch aus dem Projektordner oder direkt über seinen Dateipfad gestartet werden.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"

INDEX_FILE = DATA_DIR / "dataset_index.csv"
SET_MAPPING_FILE = DATA_DIR / "set_mapping.csv"
SETS_FILE = DATA_DIR / "official_metadata" / "sets.json"
METADATA_DIR = DATA_DIR / "official_metadata" / "cards"
OUTPUT_FILE = DATA_DIR / "dataset_metadata_matches.csv"


# Lokale Black-Star-Promo-Codes auf die offiziellen Promo-Sets abbilden.
PROMO_SET_MAPPING = {
    "xybsp": "xyp",
    "bwbsp": "bwp",
    "smbsp": "smp",
    "swshbsp": "swshp",
    "svbsp": "svp",
}

# Trainer-Gallery-Karten liegen in eigenen offiziellen Untersets.
TRAINER_GALLERY_SET_MAPPING = {
    "swsh9": "swsh9tg",
    "swsh10": "swsh10tg",
    "swsh11": "swsh11tg",
    "swsh12": "swsh12tg",
}

# Diese beiden Dataset-Ordner enthalten jeweils Karten aus zwei offiziellen
# Untersets. Die Entscheidung wird deshalb über Ordner UND Kartennummer getroffen,
# nicht allein über das Kürzel SF/CZ.
FOLDER_SUBSETS = {
    "shining-fates": {
        "special_prefix": "sv",
        "special_set": "swsh45sv",
        "base_set": "swsh45",
    },
    "crown-zenith": {
        "special_prefix": "gg",
        "special_set": "swsh12pt5gg",
        "base_set": "swsh12pt5",
    },
}

# Die neun internationalen Pikachu World Collection-Karten sind in diesem
# Projekt-Datensatz enthalten, aber nicht in den geladenen offiziellen
# Set-JSON-Dateien. Ihre PW-Nummern werden deshalb als ergänzende,
# nachvollziehbar gekennzeichnete Metadaten geführt.
WORLD_COLLECTION_CARDS = {
    "pw1": {"language": "English", "name": "Pikachu (English)"},
    "pw2": {"language": "Italian", "name": "Pikachu (Italian)"},
    "pw3": {"language": "Korean", "name": "Pikachu (Korean)"},
    "pw4": {"language": "Spanish", "name": "Pikachu (Spanish)"},
    "pw5": {"language": "Japanese", "name": "Pikachu (Japanese)"},
    "pw6": {"language": "German", "name": "Pikachu (German)"},
    "pw7": {"language": "French", "name": "Pikachu (French)"},
    "pw8": {"language": "Polish", "name": "Pikachu (Polish)"},
    "pw9": {"language": "Portuguese", "name": "Pikachu (Portuguese)"},
}


OUTPUT_EXTRA_FIELDS = [
    "official_card_id",
    "official_name",
    "official_set_id",
    "official_set_name",
    "official_number",
    "rarity",
    "supertype",
    "subtypes",
    "types",
    "artist",
    "match_status",
    "match_method",
]


def normalize(value: Any) -> str:
    """Trimmt einen Wert und vereinheitlicht ihn für Vergleiche."""
    if value is None:
        return ""
    return str(value).strip().lower()


def normalize_card_number(value: Any) -> str:
    """Normalisiert Nummern, ohne Buchstabenpräfixe oder Suffixe zu verlieren.

    Beispiele: 001 -> 1, SV085 -> sv85, GG065 -> gg65, 75a -> 75a.
    """
    value = normalize(value)
    if not value:
        return ""

    if value.isdigit():
        return str(int(value))

    match = re.fullmatch(r"([a-z]+)(\d+)", value)
    if match:
        return f"{match.group(1)}{int(match.group(2))}"

    match = re.fullmatch(r"(\d+)([a-z]+)", value)
    if match:
        return f"{int(match.group(1))}{match.group(2)}"

    return value


def normalize_promo_number(value: Any) -> str:
    """Entfernt bei Black-Star-Promo-Nummern einen vorgesetzten Seriencode.

    Beispiele: XY27 -> 27, SWSH299 -> 299, 027 -> 27.
    """
    value = normalize(value)
    if not value:
        return ""

    match = re.fullmatch(r"[a-z]*(\d+[a-z]?)", value)
    if not match:
        return value

    number = match.group(1)
    numeric_match = re.fullmatch(r"(\d+)([a-z]?)", number)
    if not numeric_match:
        return number

    return f"{int(numeric_match.group(1))}{numeric_match.group(2)}"


def join_values(value: Any) -> str:
    """Macht Listen aus Metadaten CSV-tauglich; andere Werte bleiben Text."""
    if value is None:
        return ""
    if isinstance(value, (list, tuple)):
        return ", ".join(str(item) for item in value)
    return str(value)


def load_set_mapping() -> dict[str, str]:
    """Lädt gemappte Dataset-Ordner (nur Zeilen mit status=matched)."""
    mappings: dict[str, str] = {}

    with SET_MAPPING_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        for row in csv.DictReader(file):
            folder = normalize(row.get("source_folder"))
            official_set_id = normalize(row.get("official_set_id"))
            status = normalize(row.get("status"))
            if folder and official_set_id and status == "matched":
                mappings[folder] = official_set_id

    return mappings


def load_set_names() -> dict[str, str]:
    """Lädt offizielle Set-Namen, sofern sets.json vorhanden ist."""
    if not SETS_FILE.exists():
        return {}

    with SETS_FILE.open("r", encoding="utf-8") as file:
        sets = json.load(file)

    return {
        normalize(item.get("id")): str(item.get("name", ""))
        for item in sets
        if item.get("id")
    }


def load_official_cards(set_names: dict[str, str]) -> dict[tuple[str, str], dict[str, str]]:
    """Lädt alle Karten und indiziert sie nach (offizielle Set-ID, Kartennummer)."""
    official_cards: dict[tuple[str, str], dict[str, str]] = {}
    json_files = sorted(METADATA_DIR.glob("*.json"))

    print(f"Offizielle Set-Dateien gefunden: {len(json_files)}")

    for json_file in json_files:
        try:
            with json_file.open("r", encoding="utf-8") as file:
                cards = json.load(file)
        except (OSError, json.JSONDecodeError) as error:
            print(f"WARNUNG: {json_file.name} konnte nicht geladen werden: {error}")
            continue

        if not isinstance(cards, list):
            print(f"WARNUNG: {json_file.name} enthält keine Kartenliste und wird übersprungen.")
            continue

        set_id = normalize(json_file.stem)
        set_name = set_names.get(set_id, "")

        for card in cards:
            if not isinstance(card, dict):
                continue

            original_number = str(card.get("number", "")).strip()
            number = normalize_card_number(original_number)
            if not set_id or not number:
                continue

            key = (set_id, number)
            official_cards[key] = {
                "card_id": str(card.get("id", "")),
                "name": str(card.get("name", "")),
                "set_id": set_id,
                "set_name": set_name,
                "number": original_number,
                "rarity": str(card.get("rarity", "")),
                "supertype": str(card.get("supertype", "")),
                "subtypes": join_values(card.get("subtypes", [])),
                "types": join_values(card.get("types", [])),
                "artist": str(card.get("artist", "")),
            }

    return official_cards


def build_promo_index(
    official_cards: dict[tuple[str, str], dict[str, str]],
) -> dict[tuple[str, str], dict[str, str]]:
    """Erstellt einen schnellen Index für Black-Star-Promo-Nummern."""
    promo_index: dict[tuple[str, str], dict[str, str]] = {}

    for (set_id, _), card in official_cards.items():
        if set_id not in set(PROMO_SET_MAPPING.values()):
            continue
        promo_number = normalize_promo_number(card.get("number", ""))
        if promo_number:
            promo_index[(set_id, promo_number)] = card

    return promo_index


def read_dataset_index() -> list[dict[str, str]]:
    with INDEX_FILE.open("r", encoding="utf-8-sig", newline="") as file:
        reader = csv.DictReader(file)
        required = {"image_path", "filename", "set_id", "card_number", "name", "format"}
        missing = required.difference(reader.fieldnames or [])
        if missing:
            raise ValueError(
                "Im Dataset-Index fehlen erforderliche Spalten: "
                + ", ".join(sorted(missing))
            )
        return list(reader)


def find_official_card(
    row: dict[str, str],
    set_mapping: dict[str, str],
    official_cards: dict[tuple[str, str], dict[str, str]],
    promo_index: dict[tuple[str, str], dict[str, str]],
) -> tuple[dict[str, str] | None, str]:
    """Sucht genau eine offizielle Karte mit klarer Priorität der Set-Zuordnung."""
    local_set_id = normalize(row.get("set_id"))
    local_number = normalize(row.get("card_number"))
    card_number = normalize_card_number(local_number)
    image_path = row.get("image_path", "")
    source_folder = normalize(Path(image_path).parent.name)

    if not local_set_id or not card_number:
        return None, "unparsed"

    # Ergänzende Zuordnung für die Pikachu World Collection 2010.
    # Diese Karten sind nicht Teil der offiziellen Set-JSON-Dateien;
    # der Match wird daher ausdrücklich als supplementär gekennzeichnet.
    if local_set_id == "world-collection":
        world_card = WORLD_COLLECTION_CARDS.get(card_number)
        if world_card is None:
            return None, "no_official_match"

        language = world_card["language"]
        return {
            "card_id": f"world-collection-{card_number.upper()}",
            "name": world_card["name"],
            "set_id": "world-collection",
            "set_name": "Pikachu World Collection 2010",
            "number": card_number.upper(),
            "rarity": "",
            "supertype": "Pokémon",
            "subtypes": "Basic",
            "types": "Lightning",
            "artist": "",
        }, "supplemental_world_collection"

    # Black-Star-Promos werden über ihr eigenes Promo-Set und die normalisierte
    # Promo-Nummer gesucht. Dieser Sonderweg hat Vorrang vor dem Ordner-Mapping.
    promo_set_id = PROMO_SET_MAPPING.get(local_set_id)
    if promo_set_id:
        promo_number = normalize_promo_number(local_number)
        card = promo_index.get((promo_set_id, promo_number))
        return (card, "promo") if card else (None, "no_official_match")

    # Shining Fates und Crown Zenith haben je zwei offizielle Untersets.
    # Nur in diesen beiden konkreten Ordnern wird anhand des Nummernpräfixes getrennt.
    folder_subset = FOLDER_SUBSETS.get(source_folder)
    if folder_subset:
        if card_number.startswith(folder_subset["special_prefix"]):
            mapped_set_id = folder_subset["special_set"]
        else:
            mapped_set_id = folder_subset["base_set"]

        card = official_cards.get((mapped_set_id, card_number))
        return (card, "folder_subseries") if card else (None, "no_official_match")

    # Trainer-Gallery-Karten werden nur dann in das TG-Unterset verschoben,
    # wenn sowohl die lokale Set-ID als auch das TG-Präfix passen.
    trainer_gallery_set = TRAINER_GALLERY_SET_MAPPING.get(local_set_id)
    if trainer_gallery_set and card_number.startswith("tg"):
        card = official_cards.get((trainer_gallery_set, card_number))
        return (card, "trainer_gallery") if card else (None, "no_official_match")

    # Ein vorhandenes Ordner-Mapping ist maßgeblich. Nur wenn kein Mapping
    # existiert, verwenden wir die geparste Set-ID direkt. So kann ein falsches
    # Fallback nicht versehentlich eine Karte aus einem anderen Set zuordnen.
    mapped_set_id = set_mapping.get(source_folder)
    if mapped_set_id:
        card = official_cards.get((mapped_set_id, card_number))
        return (card, "folder_mapping") if card else (None, "no_official_match")

    card = official_cards.get((local_set_id, card_number))
    return (card, "parsed_set_id") if card else (None, "no_official_match")


def main() -> None:
    print("=" * 60)
    print("DATASET ↔ OFFIZIELLE METADATEN")
    print("=" * 60)

    for required_file in (INDEX_FILE, SET_MAPPING_FILE):
        if not required_file.exists():
            raise FileNotFoundError(f"Datei nicht gefunden: {required_file}")
    if not METADATA_DIR.is_dir():
        raise FileNotFoundError(f"Metadaten-Ordner nicht gefunden: {METADATA_DIR}")

    print("\nLade Set-Mapping...")
    set_mapping = load_set_mapping()
    print(f"Gemappte Dataset-Ordner: {len(set_mapping)}")

    print("\nLade offizielle Kartendaten...")
    set_names = load_set_names()
    official_cards = load_official_cards(set_names)
    promo_index = build_promo_index(official_cards)
    print(f"Offizielle Karten geladen: {len(official_cards)}")

    print("\nLade Dataset-Index...")
    dataset_rows = read_dataset_index()
    print(f"Dataset-Bilder: {len(dataset_rows)}")

    results: list[dict[str, str]] = []
    status_counts: Counter[str] = Counter()
    method_counts: Counter[str] = Counter()
    mapping_used: Counter[str] = Counter()

    for index, row in enumerate(dataset_rows, start=1):
        official, method = find_official_card(
            row=row,
            set_mapping=set_mapping,
            official_cards=official_cards,
            promo_index=promo_index,
        )

        result = {field: row.get(field, "") for field in (
            "image_path", "filename", "set_id", "card_number", "name", "format"
        )}

        if official is None:
            status = method
            official = {}
        else:
            status = "matched"
            method_counts[method] += 1
            if method == "folder_mapping":
                folder = normalize(Path(row.get("image_path", "")).parent.name)
                mapping_used[folder] += 1

        result.update({
            "official_card_id": official.get("card_id", ""),
            "official_name": official.get("name", ""),
            "official_set_id": official.get("set_id", ""),
            "official_set_name": official.get("set_name", ""),
            "official_number": official.get("number", ""),
            "rarity": official.get("rarity", ""),
            "supertype": official.get("supertype", ""),
            "subtypes": official.get("subtypes", ""),
            "types": official.get("types", ""),
            "artist": official.get("artist", ""),
            "match_status": status,
            "match_method": method if status == "matched" else "",
        })

        status_counts[status] += 1

        if index % 1000 == 0 or index == len(dataset_rows):
            print(f"  {index}/{len(dataset_rows)}")

        results.append(result)

    fieldnames = [
        "image_path", "filename", "set_id", "card_number", "name", "format",
        *OUTPUT_EXTRA_FIELDS,
    ]
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)

    matched_count = status_counts["matched"]
    unparsed_count = status_counts["unparsed"]
    unmatched_count = status_counts["no_official_match"]
    total = len(dataset_rows)
    percentage = (matched_count / total * 100) if total else 0.0

    print("\n" + "=" * 60)
    print("ERGEBNIS")
    print("=" * 60)
    print(f"\nBilder insgesamt:       {total}")
    print(f"Eindeutig zugeordnet:   {matched_count}")
    print(f"Nicht geparst:          {unparsed_count}")
    print(f"Kein offizieller Match: {unmatched_count}")
    print(f"Zuordnungsquote:        {percentage:.2f}%")
    print(f"\nDataset-Ordner mit verwendetem Mapping: {len(mapping_used)}")

    if method_counts:
        print("\nTreffer nach Zuordnungsweg:")
        for method, count in method_counts.most_common():
            print(f"  {method}: {count}")

    print("\nErgebnis gespeichert unter:")
    print(OUTPUT_FILE)
    print("\n" + "=" * 60)
    print("ABGLEICH ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
