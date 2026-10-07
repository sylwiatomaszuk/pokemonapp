from pathlib import Path
import csv
import json
from collections import Counter


INDEX_FILE = Path("data/dataset_index.csv")
SET_MAPPING_FILE = Path("data/set_mapping.csv")
METADATA_DIR = Path("data/official_metadata/cards")
OUTPUT_FILE = Path("data/dataset_metadata_matches.csv")


def normalize(value):
    if value is None:
        return ""

    return str(value).strip().lower()


def load_set_mapping():
    """
    Lädt die Zuordnung:
    Dataset-Ordner -> offizielle Set-ID
    """

    mapping = {}

    if not SET_MAPPING_FILE.exists():
        print("WARNUNG: set_mapping.csv nicht gefunden.")
        return mapping

    with SET_MAPPING_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            if row.get("status") != "matched":
                continue

            source_folder = normalize(
                row.get("source_folder")
            )

            official_set_id = normalize(
                row.get("official_set_id")
            )

            if source_folder and official_set_id:
                mapping[source_folder] = official_set_id

    return mapping


def load_official_cards():
    """
    Lädt alle offiziellen Karten.

    Die Set-ID wird aus dem Dateinamen der JSON-Datei
    genommen, z.B.:

        swsh8.json -> swsh8
    """

    cards = {}

    json_files = sorted(
        METADATA_DIR.glob("*.json")
    )

    print(
        f"Offizielle Set-Dateien gefunden: "
        f"{len(json_files)}"
    )

    for json_file in json_files:

        set_id = normalize(
            json_file.stem
        )

        try:
            with json_file.open(
                "r",
                encoding="utf-8",
            ) as f:
                set_cards = json.load(f)

        except Exception as e:
            print(
                f"FEHLER bei {json_file.name}: {e}"
            )
            continue

        for card in set_cards:

            card_number = normalize(
                card.get("number")
            )

            if not set_id or not card_number:
                continue

            key = (
                set_id,
                card_number,
            )

            cards[key] = {
                "card_id": card.get("id", ""),
                "name": card.get("name", ""),
                "set_id": set_id,
                "set_name": "",
                "number": card.get("number", ""),
                "rarity": card.get("rarity", ""),
                "supertype": card.get("supertype", ""),
                "subtypes": ", ".join(
                    card.get("subtypes", [])
                ),
                "types": ", ".join(
                    card.get("types", [])
                ),
                "artist": card.get("artist", ""),
            }

    return cards


def get_source_folder(image_path):
    """
    Ermittelt den Dataset-Ordner aus dem Bildpfad.

    Beispiel:
    ...\\aquapolis\\aipom-aquapolis-aq-67.jpg

    -> aquapolis
    """

    path = Path(image_path)

    try:
        return normalize(
            path.parent.name
        )
    except Exception:
        return ""


def main():

    print("=" * 60)
    print("DATASET ↔ OFFIZIELLE METADATEN")
    print("=" * 60)

    if not INDEX_FILE.exists():
        print(
            f"\nFEHLER: Index nicht gefunden:\n"
            f"{INDEX_FILE}"
        )
        return

    if not METADATA_DIR.exists():
        print(
            f"\nFEHLER: Metadaten nicht gefunden:\n"
            f"{METADATA_DIR}"
        )
        return

    # ---------------------------------------------------------
    # Set-Mapping laden
    # ---------------------------------------------------------

    print("\nLade Set-Mapping...")

    set_mapping = load_set_mapping()

    print(
        f"Gemappte Dataset-Sets: "
        f"{len(set_mapping)}"
    )

    # ---------------------------------------------------------
    # Offizielle Karten laden
    # ---------------------------------------------------------

    print("\nLade offizielle Kartendaten...")

    official_cards = load_official_cards()

    print(
        f"Offizielle Karten geladen: "
        f"{len(official_cards)}"
    )

    # ---------------------------------------------------------
    # Dataset-Index laden
    # ---------------------------------------------------------

    print("\nLade Dataset-Index...")

    with INDEX_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        dataset_rows = list(
            csv.DictReader(f)
        )

    print(
        f"Dataset-Bilder: "
        f"{len(dataset_rows)}"
    )

    # ---------------------------------------------------------
    # Abgleich
    # ---------------------------------------------------------

    results = []

    status_counts = Counter()

    for index, row in enumerate(
        dataset_rows,
        start=1,
    ):

        original_set_id = normalize(
            row.get("set_id")
        )

        card_number = normalize(
            row.get("card_number")
        )

        image_path = row.get(
            "image_path",
            "",
        )

        source_folder = get_source_folder(
            image_path
        )

        # -----------------------------------------------------
        # Offizielle Set-ID bestimmen
        # -----------------------------------------------------

        official_set_id = set_mapping.get(
            source_folder
        )

        # Falls kein Mapping vorhanden ist,
        # ursprüngliche Set-ID verwenden.
        if not official_set_id:
            official_set_id = original_set_id

        result = dict(row)

        result.update(
            {
                "source_folder": source_folder,
                "mapped_set_id": official_set_id,
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
        # Keine Kartennummer
        # -----------------------------------------------------

        if not card_number:

            result["match_status"] = (
                "unparsed"
            )

            status_counts["unparsed"] += 1

            results.append(result)

            continue

        # -----------------------------------------------------
        # Exakter Match
        # -----------------------------------------------------

        key = (
            official_set_id,
            card_number,
        )

        official = official_cards.get(
            key
        )

        if official:

            result["official_card_id"] = (
                official["card_id"]
            )

            result["official_name"] = (
                official["name"]
            )

            result["official_set_id"] = (
                official["set_id"]
            )

            result["official_set_name"] = (
                official["set_name"]
            )

            result["official_number"] = (
                official["number"]
            )

            result["rarity"] = (
                official["rarity"]
            )

            result["supertype"] = (
                official["supertype"]
            )

            result["subtypes"] = (
                official["subtypes"]
            )

            result["types"] = (
                official["types"]
            )

            result["artist"] = (
                official["artist"]
            )

            result["match_status"] = (
                "matched"
            )

            status_counts["matched"] += 1

        else:

            result["match_status"] = (
                "no_official_match"
            )

            status_counts[
                "no_official_match"
            ] += 1

        results.append(result)

        if (
            index % 1000 == 0
            or index == len(dataset_rows)
        ):
            print(
                f"  {index}/"
                f"{len(dataset_rows)}"
            )

    # ---------------------------------------------------------
    # Ergebnis speichern
    # ---------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    fieldnames = [
        "image_path",
        "filename",
        "source_folder",
        "set_id",
        "mapped_set_id",
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
    # Statistik
    # ---------------------------------------------------------

    print("\n" + "=" * 60)
    print("ERGEBNIS")
    print("=" * 60)

    print(
        f"\nBilder insgesamt:       "
        f"{len(dataset_rows)}"
    )

    print(
        f"Eindeutig zugeordnet:   "
        f"{status_counts['matched']}"
    )

    print(
        f"Nicht geparst:          "
        f"{status_counts['unparsed']}"
    )

    print(
        f"Kein offizieller Match: "
        f"{status_counts['no_official_match']}"
    )

    print("\nErgebnis gespeichert unter:")
    print(
        OUTPUT_FILE.resolve()
    )

    print("\n" + "=" * 60)
    print("ABGLEICH ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()
