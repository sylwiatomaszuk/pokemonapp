from __future__ import annotations

import argparse
import csv
import re
from collections import Counter
from pathlib import Path


DEFAULT_DATASET_DIR = Path.home() / "datasets" / "pokemon-tcg"
DEFAULT_OUTPUT_FILE = Path("data/dataset_index.csv")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

WORLD_COLLECTION_NUMBERS = {
    "english": "PW1",
    "italian": "PW2",
    "korean": "PW3",
    "spanish": "PW4",
    "japanese": "PW5",
    "german": "PW6",
    "french": "PW7",
    "polish": "PW8",
    "portuguese": "PW9",
}

PROMO_SET_IDS = {
    "BW": "bwbsp",
    "XY": "xybsp",
    "SM": "smbsp",
    "SWSH": "swshbsp",
    "SV": "svbsp",
}

CSV_FIELDS = [
    "image_path",
    "filename",
    "set_id",
    "card_number",
    "name",
    "format",
]


def _result(
    set_id: str,
    card_number: str,
    name: str = "",
    format_name: str = "",
) -> dict[str, str]:
    """Create one consistently structured parser result."""
    return {
        "set_id": set_id,
        "card_number": card_number,
        "name": name,
        "format": format_name,
    }


def _clean_stem(stem: str) -> str:
    """Remove image-export timestamp suffixes without changing card data."""
    return re.sub(r"-e\d{10,}$", "", stem, flags=re.IGNORECASE)


def parse_filename(path: Path) -> dict[str, str]:
    """
    Extract set ID, card number, card name and detected filename format.

    The parser recognises the filename conventions present in the local
    Pokémon TCG image dataset. It does not verify that a parsed card exists
    in the official card metadata; that is handled by the matching script.
    """
    stem = path.stem
    clean_stem = _clean_stem(stem)
    folder = path.parent.name.lower()

    # Special cards whose filenames do not follow the usual set conventions.
    if folder == "unseen-forces" and stem in {
        "unown-unseen-forces-uf-",
        "unown-unseen-forces-uf-question-mark",
    }:
        return _result("uf", "?", "unown", "unown-special")

    if folder == "world-collection":
        match = re.fullmatch(
            r"pikachu-world-collection-(?P<language>[a-z]+)",
            stem,
            re.IGNORECASE,
        )
        if match:
            language = match.group("language").lower()
            card_number = WORLD_COLLECTION_NUMBERS.get(language)
            if card_number:
                return _result(
                    "world-collection",
                    card_number,
                    f"pikachu-{language}",
                    "world-collection-language",
                )

    # Black Star Promos: en_US-Promo_XY-XY188-shaymin.
    match = re.fullmatch(
        r"en_US-Promo_(?P<era>SWSH|BW|XY|SM|SV)-"
        r"(?P<number>(?:SWSH|BW|XY|SM|SV)\d+[a-z]?)[_-](?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        era = match.group("era").upper()
        return _result(
            PROMO_SET_IDS[era],
            match.group("number").upper(),
            match.group("name"),
            "en_US-promo-prefix-number-name",
        )

    # Scarlet & Violet promo naming conventions.
    match = re.fullmatch(r"SVP_(?P<number>\d+)_R_EN", stem, re.IGNORECASE)
    if match:
        return _result("svp", match.group("number"), "", "svp-number")

    match = re.fullmatch(
        r"(?P<set>svbsp)_en_(?P<number>\d+)"
        r"(?:[-_](?:std|out))?(?:-\d+)?",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set").lower(),
            match.group("number"),
            "",
            "svbsp-number",
        )

    # Pokémon TCG Classic deck scans and separately exported Classic images.
    match = re.fullmatch(
        r"(?P<set>clv|clb|clc)_en_(?P<number>\d+)-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set").lower(),
            match.group("number"),
            match.group("name"),
            "classic-deck",
        )

    match = re.fullmatch(
        r"Pokemon_Trading_Card_Game_Classic_(?P<number>\d+)_(?P<name>.+)",
        clean_stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            folder,
            match.group("number"),
            match.group("name"),
            "classic-special",
        )

    # Sets with a single H-number filename, e.g. skyridge/h25.jpg.
    if folder == "skyridge":
        match = re.fullmatch(r"h(?P<number>\d+)", stem, re.IGNORECASE)
        if match:
            return _result(
                "skyridge",
                f"H{match.group('number')}",
                "",
                "skyridge-h-number",
            )

    # Alph Lithograph uses written-out numbers in the HGSS filenames.
    match = re.fullmatch(
        r"en_US-(?P<set>HGSS\d+)-"
        r"(?P<number>One|Two|Three|Four)-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set").upper(),
            match.group("number").upper(),
            match.group("name"),
            "hgss-written-number",
        )

    # Older short set-code filenames, e.g. rs093-name or hl092-name.
    match = re.fullmatch(
        r"(?P<set>RS|HL|DX|SS)(?P<number>\d+)-(?P<name>.+?)(?:-\d+)?",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set").lower(),
            match.group("number"),
            match.group("name"),
            "prefix-number-name",
        )

    # Diamond & Pearl promos need a distinct promo-set ID.
    match = re.fullmatch(
        r"(?P<name>.+)-diamond-pearl-promos-(?P<number>dp\d+)",
        clean_stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            "dpp",
            match.group("number").lower(),
            match.group("name"),
            "name-diamond-pearl-promos-number",
        )

    # Filenames that include the source folder and an explicit set code.
    # Examples: swablu-platinum-pl-sh5, unown-unseen-forces-uf-l.
    if folder:
        folder_code_pattern = (
            rf"(?P<name>.+)-{re.escape(folder)}-"
            r"(?P<code>[a-z0-9]+)-"
            r"(?P<number>[a-z]{1,4}\d+[a-z]?|\d+[a-z]?|[a-z!?])"
        )
        match = re.fullmatch(folder_code_pattern, clean_stem, re.IGNORECASE)
        if match:
            return _result(
                match.group("code").lower(),
                match.group("number").upper(),
                match.group("name"),
                "name-folder-code-number",
            )

    # Filenames with source folder but no separate set-code segment.
    # Examples: ho-oh-break-xy-promos-xy154.
    if folder and folder != "diamond-pearl-promos":
        folder_number_pattern = (
            rf"(?P<name>.+)-{re.escape(folder)}-"
            r"(?P<number>[a-z]{1,4}\d+[a-z]?|\d+[a-z]?)"
        )
        match = re.fullmatch(folder_number_pattern, clean_stem, re.IGNORECASE)
        if match:
            return _result(
                folder,
                match.group("number").upper(),
                match.group("name"),
                "name-folder-number",
            )

    # Trainer Kit filenames such as lucario-tk3l-03.
    match = re.fullmatch(
        r"(?P<name>.+)-(?P<set>tk\d+[a-z]?)-(?P<number>\d+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set").lower(),
            match.group("number"),
            match.group("name"),
            "trainer-kit",
        )

    # Box Topper filenames such as p08-box-topper-suicune.
    match = re.fullmatch(
        r"(?P<number>p\d+)-box-topper-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            "box-topper",
            match.group("number").upper(),
            match.group("name"),
            "box-topper",
        )

    # Dataset-specific miscellaneous and name-number formats.
    if folder == "miscellaneous":
        match = re.fullmatch(
            r"(?:miscellaneous\.)?(?P<name>.+)-(?P<number>\d+)",
            stem,
            re.IGNORECASE,
        )
        if match:
            return _result(
                folder,
                match.group("number"),
                match.group("name"),
                "miscellaneous",
            )

    if folder == "majestic-dawn":
        match = re.fullmatch(
            r"(?P<name>[a-z_-]+?)(?P<number>\d+)",
            stem,
            re.IGNORECASE,
        )
        if match:
            return _result(
                folder,
                match.group("number"),
                match.group("name"),
                "name-number",
            )

    # Standard en_US formats. Match the most specific number patterns first.
    en_us_prefix = r"[a-z]{2}_[a-z]{2}-"
    match = re.fullmatch(
        en_us_prefix + r"(?P<set>[^-]+)-(?P<number>TG\d+)-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set"),
            match.group("number"),
            match.group("name"),
            "en_US-set-TG-number-name",
        )

    match = re.fullmatch(
        en_us_prefix + r"(?P<set>[^-]+)-(?P<number>\d+[a-z])-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set"),
            match.group("number"),
            match.group("name"),
            "en_US-set-alphanumeric-number-name",
        )

    match = re.fullmatch(
        en_us_prefix + r"(?P<set>[^-]+)-(?P<number>[a-z]{1,5}\d+)-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set"),
            match.group("number"),
            match.group("name"),
            "en_US-set-prefixed-number-name",
        )

    match = re.fullmatch(
        en_us_prefix + r"(?P<set>[^-]+)-(?P<number>\d+)-(?P<name>.+)",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("set"),
            match.group("number"),
            match.group("name"),
            "en_US-set-number-name",
        )

    # Downloaded card images named like sv3-5_en_001_std or sv1_en_050-1.
    match = re.fullmatch(
        r"(?P<set>.+)_en_(?P<number>\d+)(?:-\d+)?(?P<std>_std)?",
        stem,
        re.IGNORECASE,
    )
    if match:
        format_name = "set-en-number-std" if match.group("std") else "set-en-number"
        return _result(
            match.group("set"),
            match.group("number"),
            "",
            format_name,
        )

    # Victory Medals encode a season and a two-year Battle Road period.
    match = re.fullmatch(
        r"victory-medal-(?P<season>spring|autumn)-battle-road-(?P<start>\d{4})-(?P<end>\d{4})",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            "victory-medals",
            f"{match.group('start')}-{match.group('end')}",
            match.group("season").lower(),
            "victory-medal",
        )

    # Generic name-set-code-number, optionally followed by an image variant.
    # Example: aipom-aquapolis-aq-67 or electrode-jungle-ju-18-normal.
    match = re.fullmatch(
        r"(?P<name>.+)-(?P<set_name>[a-z0-9]+)-"
        r"(?P<code>[a-z0-9]+)-(?P<number>\d+[a-z]?)"
        r"(?:-(?:normal|reverse|holo))?",
        clean_stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            match.group("code").lower(),
            match.group("number"),
            match.group("name"),
            "name-set-code-number",
        )

    # Expedition format: h01-ampharos-expedition.
    match = re.fullmatch(
        r"h(?P<number>\d+)-(?P<name>.+)-expedition",
        stem,
        re.IGNORECASE,
    )
    if match:
        return _result(
            "expedition",
            match.group("number"),
            match.group("name"),
            "h-number-name-set",
        )

    return _result("", "", "", "unknown")


def build_index(dataset_dir: Path) -> tuple[list[dict[str, str]], Counter]:
    """Parse every supported image in the dataset and return CSV rows."""
    if not dataset_dir.is_dir():
        raise FileNotFoundError(f"Dataset-Verzeichnis nicht gefunden: {dataset_dir}")

    image_paths = sorted(
        path
        for path in dataset_dir.rglob("*")
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    )

    rows = []
    format_counts = Counter()

    for index, image_path in enumerate(image_paths, start=1):
        parsed = parse_filename(image_path)
        rows.append(
            {
                "image_path": str(image_path),
                "filename": image_path.name,
                **parsed,
            }
        )
        format_counts[parsed["format"]] += 1

        if index % 1000 == 0 or index == len(image_paths):
            print(f"  {index}/{len(image_paths)}")

    return rows, format_counts


def write_index(rows: list[dict[str, str]], output_file: Path) -> None:
    """Write parsed rows to the dataset index CSV."""
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Erstellt einen CSV-Index der lokalen Pokémon-TCG-Bilder."
    )
    parser.add_argument(
        "--dataset-dir",
        type=Path,
        default=DEFAULT_DATASET_DIR,
        help=f"Bilddatensatz (Standard: {DEFAULT_DATASET_DIR})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT_FILE,
        help=f"Ziel-CSV (Standard: {DEFAULT_OUTPUT_FILE})",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("POKÉMON DATASET INDEX")
    print("=" * 60)
    print(f"\nDatensatz: {args.dataset_dir}")

    try:
        rows, format_counts = build_index(args.dataset_dir)
    except FileNotFoundError as error:
        parser.error(str(error))
        return

    unknown_count = format_counts["unknown"]
    parsed_count = len(rows) - unknown_count

    write_index(rows, args.output)

    print("\nVerteilung:")
    print("-" * 60)
    for format_name, count in format_counts.most_common():
        print(f"{format_name:40} {count:6}")

    print("\nZusammenfassung:")
    print(f"  Gesamtbilder:        {len(rows)}")
    print(f"  Erfolgreich geparst: {parsed_count}")
    print(f"  Nicht erkannt:       {unknown_count}")
    if rows:
        print(f"  Erkennungsquote:     {parsed_count / len(rows) * 100:.2f}%")

    print("\nIndex gespeichert unter:")
    print(args.output.resolve())

    if unknown_count:
        print("\nBeispiele nicht erkannter Dateien:")
        shown = 0
        for row in rows:
            if row["format"] == "unknown":
                print(f"  {row['filename']}")
                shown += 1
                if shown == 20:
                    break

    print("\n" + "=" * 60)
    print("INDEX ERSTELLT")
    print("=" * 60)


if __name__ == "__main__":
    main()
