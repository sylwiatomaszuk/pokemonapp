from pathlib import Path
import csv
import json
from collections import Counter


INDEX_FILE = Path("data/dataset_index.csv")
METADATA_DIR = Path("data/official_metadata/cards")
OUTPUT_FILE = Path("data/dataset_metadata_matches.csv")


def normalize(value):
    """Vereinheitlicht Werte für den Vergleich."""
    if value is None:
        return ""

    return str(value).strip().lower()


def normalize_card_number(value):
    """
    Normalisiert Kartennummern für den Vergleich.

    Beispiele:
        001  -> 1
        01   -> 1
        1    -> 1
        020  -> 20

    Sondernummern bleiben erhalten:
        TG001 -> tg001
        SV001 -> sv001
        75a   -> 75a
    """
    value = normalize(value)

    if not value:
        return ""

    if value.isdigit():
        return str(int(value))

    return value


def load_official_cards():
    """
    Lädt alle offiziellen Karten aus den vorhandenen
    Set-JSON-Dateien.

    Rückgabe:
        Dictionary mit:
        (set_id, normalisierte_kartennummer) -> Karten-Metadaten
    """

    cards = {}

    json_files = sorted(METADATA_DIR.glob("*.json"))

    print(f"Offizielle Set-Dateien gefunden: {len(json_files)}")

    for json_file in json_files:
        try:
            with json_file.open("r", encoding="utf-8") as f:
                set_cards = json.load(f)

        except Exception as e:
            print(f"FEHLER bei {json_file.name}: {e}")
            continue

        for card in set_cards:
            # Die Set-ID kommt bei unseren offiziellen JSON-Dateien
            # aus dem Dateinamen, z. B. swsh10.json -> swsh10.
            set_id = normalize(json_file.stem)

            number = normalize_card_number(card.get("number"))

            if not set_id or not number:
                continue

            key = (set_id, number)

            cards[key] = {
                "card_id": card.get("id", ""),
                "name": card.get("name", ""),
                "set_id": card.get("set", {}).get("id", ""),
                "set_name": card.get("set", {}).get("name", ""),
                "number": card.get("number", ""),
                "rarity": card.get("rarity", ""),
                "supertype": card.get("supertype", ""),
                "subtypes": ", ".join(card.get("subtypes", [])),
                "types": ", ".join(card.get("types", [])),
                "artist": card.get("artist", ""),
            }

    return cards


def main():
    print("=" * 60)
    print("DATASET ↔ OFFIZIELLE METADATEN")
    print("=" * 60)

    if not INDEX_FILE.exists():
        print("\nFEHLER:")
        print(f"Index nicht gefunden: {INDEX_FILE}")
        return

    if not METADATA_DIR.exists():
        print("\nFEHLER:")
        print(f"Metadaten nicht gefunden: {METADATA_DIR}")
        return

    # ---------------------------------------------------------
    # 1. Offizielle Karten laden
    # ---------------------------------------------------------

    print("\nLade offizielle Kartendaten...")

    official_cards = load_official_cards()

    print(f"Offizielle Karten geladen: {len(official_cards)}")

    # ---------------------------------------------------------
    # 2. Dataset-Index laden
    # ---------------------------------------------------------

    print("\nLade Dataset-Index...")

    with INDEX_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:
        reader = csv.DictReader(f)
        dataset_rows = list(reader)

    print(f"Dataset-Bilder: {len(dataset_rows)}")

    # ---------------------------------------------------------
    # 3. Abgleich
    # ---------------------------------------------------------

    results = []

    status_counts = Counter()

    for index, row in enumerate(dataset_rows, start=1):

        set_id = normalize(row.get("set_id"))
        card_number = normalize_card_number(row.get("card_number"))

        result = dict(row)

        result.update(
            {
                "official_card_id": "",
                "official_name": "",
                "official_set_id": "",
                "official_set_name": "",
                "official_number": "",
                "rarity": "",
                "supertype": "",
                "subtypes": "",
                "types": "",
                "artist": "",
                "match_status": "",
            }
        )

        # -----------------------------------------------------
        # Kein Parser-Ergebnis vorhanden
        # -----------------------------------------------------

        if not set_id or not card_number:
            result["match_status"] = "unparsed"

            status_counts["unparsed"] += 1
            results.append(result)
            continue

        # -----------------------------------------------------
        # Abgleich Set + normalisierte Kartennummer
        # -----------------------------------------------------

        key = (
            set_id,
            card_number,
        )

        official = official_cards.get(key)

        if official is not None:

            result["official_card_id"] = official["card_id"]
            result["official_name"] = official["name"]
            result["official_set_id"] = official["set_id"]
            result["official_set_name"] = official["set_name"]
            result["official_number"] = official["number"]
            result["rarity"] = official["rarity"]
            result["supertype"] = official["supertype"]
            result["subtypes"] = official["subtypes"]
            result["types"] = official["types"]
            result["artist"] = official["artist"]

            result["match_status"] = "matched"

            status_counts["matched"] += 1

        else:
            result["match_status"] = "no_official_match"

            status_counts["no_official_match"] += 1

        results.append(result)

        if index % 1000 == 0 or index == len(dataset_rows):
            print(f"  {index}/{len(dataset_rows)}")

    # ---------------------------------------------------------
    # 4. Ergebnis speichern
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        "image_path",
        "filename",
        "set_id",
        "card_number",
        "name",
        "format",
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
    ]

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=fieldnames,
        )

        writer.writeheader()
        writer.writerows(results)

    # ---------------------------------------------------------
    # 5. Statistik
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("ERGEBNIS")
    print("=" * 60)

    print(f"\nBilder insgesamt:       {len(dataset_rows)}")
    print(f"Eindeutig zugeordnet:   {status_counts['matched']}")
    print(f"Nicht geparst:          {status_counts['unparsed']}")
    print(f"Kein offizieller Match: {status_counts['no_official_match']}")

    print("\nErgebnis gespeichert unter:")
    print(OUTPUT_FILE.resolve())

    print("\n" + "=" * 60)
    print("ABGLEICH ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
