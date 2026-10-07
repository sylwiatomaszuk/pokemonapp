from pathlib import Path
from collections import Counter
import re


DATASET_DIR = Path(
    r"C:\Users\sylwi\Documents\PokemonData\Pokemon TCG\Pokemon TCG"
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def analyze_filename(path: Path):
    """
    Unterstützt mehrere bekannte Dateinamen-Formate.

    Format 1:
    en_US-XY7-001-oddish.jpg

    Format 2:
    sv3-5_en_001_std.jpg
    """

    stem = path.stem

    # ---------------------------------------------------------
    # FORMAT 1
    # en_US-XY7-001-oddish
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<language>[a-z]{2}_[A-Z]{2})-"
        r"(?P<set_id>[^-]+)-"
        r"(?P<number>\d+)-"
        r"(?P<name>.+)$",
        stem,
    )

    if match:
        return {
            "format": "en_US-set-number-name",
            "language": match.group("language"),
            "set_id": match.group("set_id"),
            "number": match.group("number"),
            "name": match.group("name"),
        }

    # ---------------------------------------------------------
    # FORMAT 2
    # sv3-5_en_001_std
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<set_id>.+)_en_(?P<number>\d+)_std$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "format": "set_en_number_std",
            "language": "en",
            "set_id": match.group("set_id"),
            "number": match.group("number"),
            "name": None,
        }

    return None


def main():
    print("=" * 60)
    print("DATEINAMEN-ANALYSE DES POKÉMON-DATENSATZES")
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

    parsed = []
    failed = []

    for path in files:
        result = analyze_filename(path)

        if result is None:
            failed.append(path)
        else:
            parsed.append((path, result))

    print("\nErgebnis der Dateinamen-Erkennung:")
    print(f"  Erfolgreich erkannt: {len(parsed)}")
    print(f"  Nicht erkannt:       {len(failed)}")

    # Sets
    set_counts = Counter(
        result["set_id"]
        for _, result in parsed
    )

    print("\nErkannte Set-IDs:")
    print(f"  Anzahl verschiedene Sets: {len(set_counts)}")

    for set_id, count in set_counts.most_common():
        print(f"  {set_id}: {count}")

    # Sprachen
    language_counts = Counter(
        result["language"]
        for _, result in parsed
    )

    print("\nSprachen:")
    for language, count in language_counts.most_common():
        print(f"  {language}: {count}")

    # Nicht erkannte Dateien
    if failed:
        print("\nNicht erkannte Dateinamen:")

        for path in failed[:50]:
            print(f"  {path}")

        if len(failed) > 50:
            print(f"  ... und {len(failed) - 50} weitere")

    # Beispiele
    print("\nBeispiele erfolgreicher Erkennung:")

    for path, result in parsed[:10]:
        print(f"\n  Datei: {path.name}")
        print(f"    Set:      {result['set_id']}")
        print(f"    Nummer:   {result['number']}")
        print(f"    Name:     {result['name']}")
        print(f"    Sprache:  {result['language']}")

    print("\n" + "=" * 60)
    print("ANALYSE FERTIG")
    print("=" * 60)


if __name__ == "__main__":
    main()