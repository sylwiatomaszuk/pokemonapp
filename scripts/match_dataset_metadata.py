from pathlib import Path

import csv
import json
import re
from collections import Counter


INDEX_FILE = Path("data/dataset_index.csv")
SET_MAPPING_FILE = Path("data/set_mapping.csv")

METADATA_DIR = Path("data/official_metadata/cards")
OUTPUT_FILE = Path("data/dataset_metadata_matches.csv")


PROMO_SET_MAPPING = {
    "xybsp": "xyp",
    "bwbsp": "bwp",
    "smbsp": "smp",
    "swshbsp": "swshp",
    "svbsp": "svp",
}


FILENAME_SET_MAPPING = {
    "swsh9": "swsh9tg",
    "swsh10": "swsh10tg",
    "swsh11": "swsh11tg",
    "swsh12": "swsh12tg",
}


def normalize(value):
    """Vereinheitlicht Werte für den Vergleich."""

    if value is None:
        return ""

    return str(value).strip().lower()


def normalize_card_number(value):
    """
    Normalisiert Kartennummern für den normalen Vergleich.

    Beispiele:

        001   -> 1
        01    -> 1
        020   -> 20
        TG001 -> tg1
        TG030 -> tg30
        SV001 -> sv1
        75a   -> 75a
    """

    value = normalize(value)

    if not value:
        return ""

    if value.isdigit():
        return str(int(value))

    match = re.fullmatch(
        r"([a-z]+)(\d+)",
        value,
    )

    if match:

        prefix = match.group(1)
        number = match.group(2)

        return (
            prefix
            + str(int(number))
        )

    return value


def normalize_promo_card_number(value):
    """
    Normalisiert Kartennummern von Black-Star-Promos.

    Offizielle Metadaten verwenden zum Beispiel:

        XY27
        BW97
        SM04
        SWSH299

    Das Dataset verwendet dagegen:

        027
        097
        004
        299

    Für den Vergleich wird deshalb der Buchstaben-Präfix
    entfernt und nur die eigentliche Nummer verglichen.

    Beispiele:

        027     -> 27
        XY27    -> 27
        097     -> 97
        BW97    -> 97
        004     -> 4
        SM04    -> 4
        299     -> 299
        SWSH299 -> 299
    """

    value = normalize(value)

    if not value:
        return ""

    match = re.fullmatch(
        r"[a-z]*(\d+[a-z]?)",
        value,
    )

    if not match:
        return value

    number = match.group(1)

    number_match = re.fullmatch(
        r"(\d+)([a-z]?)",
        number,
    )

    if not number_match:
        return number

    numeric_part = str(
        int(number_match.group(1))
    )

    suffix = number_match.group(2)

    return (
        numeric_part
        + suffix
    )


def load_set_mapping():
    """
    Lädt die Zuordnung unserer Dataset-Ordner zu den
    offiziellen Pokémon-TCG-Set-IDs.
    """

    mappings = {}

    if not SET_MAPPING_FILE.exists():

        print(
            f"FEHLER: Set-Mapping nicht gefunden: "
            f"{SET_MAPPING_FILE}"
        )

        return mappings

    with SET_MAPPING_FILE.open(
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        for row in reader:

            source_folder = normalize(
                row.get("source_folder")
            )

            official_set_id = normalize(
                row.get("official_set_id")
            )

            status = normalize(
                row.get("status")
            )

            if (
                source_folder
                and official_set_id
                and status == "matched"
            ):

                mappings[
                    source_folder
                ] = official_set_id

    return mappings


def load_official_cards():
    """
    Lädt alle offiziellen Karten aus den vorhandenen
    Set-JSON-Dateien.
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

        # Set-ID aus dem Dateinamen.
        #
        # Beispiel:
        # swsh10.json -> swsh10

        set_id = normalize(
            json_file.stem
        )

        for card in set_cards:

            number = normalize_card_number(
                card.get("number")
            )

            if not set_id or not number:
                continue

            key = (
                set_id,
                number,
            )

            cards[key] = {
                "card_id": card.get(
                    "id",
                    "",
                ),

                "name": card.get(
                    "name",
                    "",
                ),

                "set_id": set_id,

                "set_name": "",

                "number": card.get(
                    "number",
                    "",
                ),

                "rarity": card.get(
                    "rarity",
                    "",
                ),

                "supertype": card.get(
                    "supertype",
                    "",
                ),

                "subtypes": ", ".join(
                    card.get(
                        "subtypes",
                        [],
                    )
                ),

                "types": ", ".join(
                    card.get(
                        "types",
                        [],
                    )
                ),

                "artist": card.get(
                    "artist",
                    "",
                ),
            }

    return cards


def find_promo_card(
    official_cards,
    promo_set_id,
    dataset_card_number,
):
    """
    Sucht eine Karte gezielt innerhalb eines Promo-Sets.

    Beispiel:

        Dataset:
        xybsp + 027

        Offizielle Daten:
        xyp + XY27

        Ergebnis:
        xyp-XY27
    """

    target_number = normalize_promo_card_number(
        dataset_card_number
    )

    if not target_number:
        return None

    for (
        official_set_id,
        official_number,
    ), card in official_cards.items():

        if official_set_id != promo_set_id:
            continue

        normalized_official_number = (
            normalize_promo_card_number(
                official_number
            )
        )

        if (
            normalized_official_number
            == target_number
        ):

            return card

    return None


def main():

    print("=" * 60)
    print("DATASET ↔ OFFIZIELLE METADATEN")
    print("=" * 60)

    if not INDEX_FILE.exists():

        print("\nFEHLER:")

        print(
            f"Index nicht gefunden: "
            f"{INDEX_FILE}"
        )

        return

    if not SET_MAPPING_FILE.exists():

        print("\nFEHLER:")

        print(
            f"Set-Mapping nicht gefunden: "
            f"{SET_MAPPING_FILE}"
        )

        return

    if not METADATA_DIR.exists():

        print("\nFEHLER:")

        print(
            f"Metadaten nicht gefunden: "
            f"{METADATA_DIR}"
        )

        return

    print("\nLade Set-Mapping...")

    set_mapping = load_set_mapping()

    print(
        f"Gemappte Dataset-Ordner: "
        f"{len(set_mapping)}"
    )

    print("\nLade offizielle Kartendaten...")

    official_cards = load_official_cards()

    print(
        f"Offizielle Karten geladen: "
        f"{len(official_cards)}"
    )

    print("\nLade Dataset-Index...")

    with INDEX_FILE.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as f:

        reader = csv.DictReader(f)

        dataset_rows = list(reader)

    print(
        f"Dataset-Bilder: "
        f"{len(dataset_rows)}"
    )

    results = []

    status_counts = Counter()

    mapping_used = Counter()

    promo_matches = Counter()

    for index, row in enumerate(
        dataset_rows,
        start=1,
    ):

        set_id = normalize(
            row.get("set_id")
        )

        original_card_number = normalize(
            row.get("card_number")
        )

        card_number = normalize_card_number(
            original_card_number
        )

        image_path = row.get(
            "image_path",
            "",
        )

        source_folder = normalize(
            Path(image_path).parent.name
        )

        # --------------------------------------------------
        # Ergebniszeile vorbereiten
        # --------------------------------------------------

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

        # --------------------------------------------------
        # Unvollständige Dataset-Daten
        # --------------------------------------------------

        if not set_id or not card_number:

            result["match_status"] = "unparsed"

            status_counts[
                "unparsed"
            ] += 1

            results.append(
                result
            )

            continue

        # --------------------------------------------------
        # Promo-Matching
        #
        # Wichtig:
        # Hier verwenden wir set_id und NICHT
        # source_folder.
        #
        # Beispiel:
        #
        # set_id = xybsp
        # source_folder = xy-promos
        #
        # xybsp wird direkt zu xyp gemappt.
        # --------------------------------------------------

        is_promo = (
            set_id in PROMO_SET_MAPPING
        )

        if is_promo:

            promo_set_id = PROMO_SET_MAPPING[
                set_id
            ]

            official = find_promo_card(
                official_cards,
                promo_set_id,
                original_card_number,
            )

            if official is not None:

                promo_matches[
                    promo_set_id
                ] += 1

        else:

            # --------------------------------------------------
            # Normales Matching
            # --------------------------------------------------

            if (
                set_id in FILENAME_SET_MAPPING
                and card_number.startswith("tg")
            ):

                mapped_set_id = (
                    FILENAME_SET_MAPPING[
                        set_id
                    ]
                )

            elif source_folder in set_mapping:

                mapped_set_id = set_mapping[
                    source_folder
                ]

                mapping_used[
                    source_folder
                ] += 1

            else:

                mapped_set_id = set_id

            mapped_set_id = normalize(
                mapped_set_id
            )

            key = (
                mapped_set_id,
                card_number,
            )

            official = official_cards.get(
                key
            )

        # --------------------------------------------------
        # Treffer verarbeiten
        # --------------------------------------------------

        if official is not None:

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

            result["match_status"] = "matched"

            status_counts[
                "matched"
            ] += 1

        else:

            result["match_status"] = (
                "no_official_match"
            )

            status_counts[
                "no_official_match"
            ] += 1

        results.append(
            result
        )

        if (
            index % 1000 == 0
            or index == len(dataset_rows)
        ):

            print(
                f"  {index}/{len(dataset_rows)}"
            )

    # ------------------------------------------------------
    # CSV schreiben
    # ------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

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

        writer.writerows(
            results
        )

    # ------------------------------------------------------
    # Ergebnis
    # ------------------------------------------------------

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

    print(
        f"\nDataset-Ordner mit Mapping: "
        f"{len(mapping_used)}"
    )

    print("\nPromo-Treffer:")

    for set_id, count in sorted(
        promo_matches.items()
    ):

        print(
            f"  {set_id}: {count}"
        )

    print(
        "\nErgebnis gespeichert unter:"
    )

    print(
        OUTPUT_FILE.resolve()
    )

    print("\n" + "=" * 60)
    print("ABGLEICH ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    main()