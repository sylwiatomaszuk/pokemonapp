from pathlib import Path
from collections import Counter
import re


DATASET_DIR = Path(
    r"C:\Users\sylwi\Documents\PokemonData\Pokemon TCG\Pokemon TCG"
)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def classify_known_filename(stem: str):
    if re.match(
        r"^[a-z]{2}_[A-Z]{2}-[^-]+-\d+-.+$",
        stem,
    ):
        return True

    if re.match(
        r"^.+_en_\d+_std$",
        stem,
        re.IGNORECASE,
    ):
        return True

    if re.match(
        r"^.+-[a-z0-9]+-[a-z]+-\d+[a-z]?$",
        stem,
        re.IGNORECASE,
    ):
        return True

    if re.match(
        r"^h\d+-.*-expedition$",
        stem,
        re.IGNORECASE,
    ):
        return True

    if re.match(
        r"^[a-z]{2}_[A-Z]{2}-[^-]+-\d+[a-z]?-.*$",
        stem,
    ):
        return True

    return False


def simplify_pattern(stem: str):
    """
    Ersetzt variable Bestandteile durch Platzhalter,
    damit ähnliche Dateinamen gruppiert werden.
    """

    parts = stem.split("-")

    simplified = []

    for part in parts:
        if part.isdigit():
            simplified.append("<NUMBER>")
        elif re.fullmatch(r"\d+[a-z]", part, re.IGNORECASE):
            simplified.append("<NUMBER_LETTER>")
        elif "_" in part:
            simplified.append(part)
        else:
            simplified.append(part)

    return "-".join(simplified)


def main():
    print("=" * 60)
    print("ANALYSE DER UNBEKANNTEN DATEINAMEN")
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

    unknown = []

    for path in files:
        if not classify_known_filename(path.stem):
            unknown.append(path)

    print(f"\nBilder insgesamt: {len(files)}")
    print(f"Unbekannte Dateien: {len(unknown)}")

    patterns = Counter()

    for path in unknown:
        pattern = simplify_pattern(path.stem)
        patterns[pattern] += 1

    print("\nHäufigste unbekannte Muster:")
    print("-" * 80)

    for pattern, count in patterns.most_common(50):
        print(f"{count:5}  {pattern}")

    print("\nBeispiele der häufigsten Muster:")
    print("-" * 80)

    shown = set()

    for path in unknown:
        pattern = simplify_pattern(path.stem)

        if pattern not in shown and len(shown) < 50:
            print(f"\nMuster: {pattern}")
            print(f"Beispiel: {path.name}")
            shown.add(pattern)

    print("\n" + "=" * 60)
    print("ANALYSE FERTIG")
    print("=" * 60)


if __name__ == "__main__":
    main()