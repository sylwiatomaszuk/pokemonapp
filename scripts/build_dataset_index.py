from pathlib import Path
from collections import Counter
import csv
import re


DATASET_DIR = Path(
    r"C:\Users\sylwi\Documents\PokemonData\Pokemon TCG\Pokemon TCG"
)

OUTPUT_FILE = Path("data/dataset_index.csv")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def parse_filename(path: Path):
    """
    Versucht verschiedene bekannte Dateinamenformate
    auf eine gemeinsame Struktur abzubilden.

    Ergebnis:
        set_id
        card_number
        name
        format
    """

    stem = path.stem

    # ---------------------------------------------------------
    # 1. en_US-XY7-001-oddish
    # ---------------------------------------------------------
    match = re.match(
        r"^[a-z]{2}_[A-Z]{2}-(?P<set>[^-]+)-"
        r"(?P<number>\d+)-(?P<name>.+)$",
        stem,
    )

    if match:
        return {
            "set_id": match.group("set"),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "en_US-set-number-name",
        }

    # ---------------------------------------------------------
    # 2. en_US-XY7-75a-hex_maniac-yaa
    # ---------------------------------------------------------
    match = re.match(
        r"^[a-z]{2}_[A-Z]{2}-(?P<set>[^-]+)-"
        r"(?P<number>\d+[a-z])-(?P<name>.+)$",
        stem,
    )

    if match:
        return {
            "set_id": match.group("set"),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "en_US-set-alphanumeric-number-name",
        }

    # ---------------------------------------------------------
    # 3. en_US-SWSH10-TG001-abomasnow
    # ---------------------------------------------------------
    match = re.match(
        r"^[a-z]{2}_[A-Z]{2}-(?P<set>[^-]+)-"
        r"(?P<number>TG\d+)-(?P<name>.+)$",
        stem,
    )

    if match:
        return {
            "set_id": match.group("set"),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "en_US-set-TG-number-name",
        }

    # ---------------------------------------------------------
    # 4. sv3-5_en_001_std
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<set>.+)_en_(?P<number>\d+)_std$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set"),
            "card_number": match.group("number"),
            "name": "",
            "format": "set-en-number-std",
        }

    # ---------------------------------------------------------
    # 5. name-set-code-number
    #
    # Beispiel:
    # aipom-aquapolis-aq-67
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<name>.+)-(?P<set_name>[a-z0-9]+)-"
        r"(?P<set_code>[a-z0-9]+)-(?P<number>\d+[a-z]?)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set_code"),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "name-set-code-number",
        }

    # ---------------------------------------------------------
    # 6. Expedition h01-ampharos-expedition
    # ---------------------------------------------------------
    match = re.match(
        r"^h(?P<number>\d+)-(?P<name>.+)-expedition$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": "expedition",
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "h-number-name-set",
        }

    # ---------------------------------------------------------
    # Nicht erkannt
    # ---------------------------------------------------------
    return {
        "set_id": "",
        "card_number": "",
        "name": "",
        "format": "unknown",
    }


def main():
    print("=" * 60)
    print("POKÉMON DATASET INDEX")
    print("=" * 60)

    if not DATASET_DIR.exists():
        print("\nFEHLER: Datensatz nicht gefunden:")
        print(DATASET_DIR)
        return

    files = [
        p
        for p in DATASET_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    ]

    print(f"\nBilder gefunden: {len(files)}")

    rows = []
    format_counts = Counter()
    unknown_files = []

    for index, path in enumerate(files, start=1):
        parsed = parse_filename(path)

        row = {
            "image_path": str(path),
            "filename": path.name,
            "set_id": parsed["set_id"],
            "card_number": parsed["card_number"],
            "name": parsed["name"],
            "format": parsed["format"],
        }

        rows.append(row)

        format_counts[parsed["format"]] += 1

        if parsed["format"] == "unknown":
            unknown_files.append(path)

        if index % 1000 == 0 or index == len(files):
            print(f"  {index}/{len(files)}")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_FILE.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as f:

        writer = csv.DictWriter(
            f,
            fieldnames=[
                "image_path",
                "filename",
                "set_id",
                "card_number",
                "name",
                "format",
            ],
        )

        writer.writeheader()
        writer.writerows(rows)

    print("\nVerteilung:")
    print("-" * 60)

    for format_name, count in format_counts.most_common():
        print(f"{format_name:40} {count:6}")

    print("\nZusammenfassung:")
    print(f"  Gesamtbilder:        {len(files)}")
    print(f"  Erfolgreich geparst: {len(files) - len(unknown_files)}")
    print(f"  Nicht erkannt:       {len(unknown_files)}")

    print("\nIndex gespeichert unter:")
    print(OUTPUT_FILE.resolve())

    if unknown_files:
        print("\nBeispiele nicht erkannter Dateien:")

        for path in unknown_files[:20]:
            print(f"  {path.name}")

    print("\n" + "=" * 60)
    print("INDEX ERSTELLT")
    print("=" * 60)


if __name__ == "__main__":
    main()