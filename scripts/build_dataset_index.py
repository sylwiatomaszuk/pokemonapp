
from pathlib import Path
from collections import Counter
import csv
import re


DATASET_DIR = Path.home() / "datasets" / "pokemon-tcg"

OUTPUT_FILE = Path("data/dataset_index.csv")

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def parse_filename(path: Path):
    """
    Erkennt verschiedene bekannte Dateinamenformate
    und ordnet sie einer gemeinsamen Struktur zu.

    Ergebnis:
        set_id
        card_number
        name
        format
    """

    stem = path.stem
    folder = path.parent.name.lower()

        # Unown Fragezeichen-Form aus Unseen Forces
    if folder == "unseen-forces" and stem == "unown-unseen-forces-uf-":
        return {
            "set_id": "uf",
            "card_number": "?",
            "name": "unown",
            "format": "unown-special",
        }

        # ---------------------------------------------------------
    # 1. Unown mit ausgeschriebener Fragezeichen-Kartennummer
    # ---------------------------------------------------------
    if folder == "unseen-forces" and stem == "unown-unseen-forces-uf-question-mark":
        return {
            "set_id": "uf",
            "card_number": "?",
            "name": "unown",
            "format": "unown-special",
        }

    # ---------------------------------------------------------
    # 2. Pokémon World Collection
    # Beispiel: pikachu-world-collection-spanish
    # Sprache bleibt im Namen erhalten.
    # ---------------------------------------------------------
    match = re.match(
        r"^pikachu-world-collection-(?P<language>[a-z]+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": "world-collection",
            "card_number": "",
            "name": "pikachu-" + match.group("language").lower(),
            "format": "world-collection-language",
        }

    # Zeitstempel und bekannte Bildvarianten entfernen
    clean_stem = re.sub(r"-e\d{10,}$", "", stem, flags=re.IGNORECASE)

    # ---------------------------------------------------------
    # 1. Erweiterte Black-Star-Promos mit Buchstabensuffix
    # ---------------------------------------------------------
    match = re.match(
        r"^en_US-Promo_(?P<era>SWSH|BW|XY|SM|SV)-"
        r"(?P<number>(?:SWSH|BW|XY|SM|SV)\d+[a-z]?)[_-](?P<name>.+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        promo_ids = {
            "SWSH": "swshbsp",
            "BW": "bwbsp",
            "XY": "xybsp",
            "SM": "smbsp",
            "SV": "svbsp",
        }

        return {
            "set_id": promo_ids[match.group("era").upper()],
            "card_number": match.group("number").upper(),
            "name": match.group("name"),
            "format": "extended-promo",
        }

    # ---------------------------------------------------------
    # 2. Scarlet & Violet Promo-Dateien
    # Beispiel: SVP_209_R_EN
    # ---------------------------------------------------------
    match = re.match(
        r"^SVP_(?P<number>\d+)_R_EN$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": "svp",
            "card_number": match.group("number"),
            "name": "",
            "format": "svp-number",
        }

    # ---------------------------------------------------------
    # 3. SV Black-Star-Promo-Dateien
    # Beispiele:
    # svbsp_en_125-out
    # svbsp_en_149_std-1
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<set>svbsp)_en_(?P<number>\d+)"
        r"(?:[-_](?:std|out))?(?:-\d+)?$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set").lower(),
            "card_number": match.group("number"),
            "name": "",
            "format": "svbsp-number",
        }

    # ---------------------------------------------------------
    # 4. Pokémon TCG Classic
    # Beispiele:
    # clv_en_030-ultra_ball
    # clb_en_027-rockets_admin
    # clc_en_003-charizard
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<set>cl[vbc])_en_(?P<number>\d+)-(?P<name>.+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set").lower(),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "classic-deck",
        }

    # ---------------------------------------------------------
    # 5. Zusätzliche Pokémon TCG Classic-Dateien
    # Beispiel:
    # Pokemon_Trading_Card_Game_Classic_17_Lugia_ex
    # ---------------------------------------------------------
    match = re.match(
        r"^Pokemon_Trading_Card_Game_Classic_"
        r"(?P<number>\d+)_(?P<name>.+)$",
        clean_stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": folder,
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "classic-special",
        }

    # ---------------------------------------------------------
    # 6. Skyridge: einzelne H-Kartennummern
    # Beispiel: h25.jpg
    # ---------------------------------------------------------
    if folder == "skyridge":
        match = re.fullmatch(
            r"h(?P<number>\d+)",
            stem,
            re.IGNORECASE,
        )

        if match:
            return {
                "set_id": "skyridge",
                "card_number": "H" + match.group("number"),
                "name": "",
                "format": "skyridge-h-number",
            }

    # ---------------------------------------------------------
    # 7. Ältere Sets: Setcode + Nummer + Kartenname
    # Beispiele:
    # rs093-darkness_energy-1
    # hl092-stevens_advice
    # dx009-jirachi
    # ss088-wobbuffet
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<set>RS|HL|DX|SS)(?P<number>\d+)-"
        r"(?P<name>.+?)(?:-\d+)?$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set").lower(),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "prefix-number-name",
        }

    # ---------------------------------------------------------
    # 8. Ältere Sets mit ausgeschriebener Kartennummer
    # Beispiele:
    # HGSS2-Two-alph_lithograph
    # HGSS4-Four-alph_lithograph
    # ---------------------------------------------------------
    match = re.match(
        r"^en_US-(?P<set>HGSS\d+)-"
        r"(?P<number>One|Two|Three|Four)-(?P<name>.+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set").upper(),
            "card_number": match.group("number").upper(),
            "name": match.group("name"),
            "format": "hgss-written-number",
        }

    # ---------------------------------------------------------
    # 9. Name – Dataset-Ordner – Setcode – Kartennummer
    #
    # Beispiele:
    # swablu-platinum-pl-sh5
    # drifloon-stormfront-sf-sh1
    # frost-rotom-rising-rivals-rr-rt2
    # arceus-colorless-arceus-ar-ar5
    # unown-unseen-forces-uf-l
    # ---------------------------------------------------------
    if folder:
        match = re.match(
            rf"^(?P<name>.+)-{re.escape(folder)}-"
            r"(?P<code>[a-z0-9]+)-"
            r"(?P<number>[a-z]{1,4}\d+[a-z]?|\d+[a-z]?|[a-z!?])$",
            clean_stem,
            re.IGNORECASE,
        )

        if match:
            return {
                "set_id": match.group("code").lower(),
                "card_number": match.group("number").upper(),
                "name": match.group("name"),
                "format": "name-folder-code-number",
            }

    # ---------------------------------------------------------
    # 10. Name – Dataset-Ordner – Kartennummer
    # Beispiel:
    # ho-oh-break-xy-promos-xy154
    # ---------------------------------------------------------
    if folder and folder != "diamond-pearl-promos":
        match = re.match(
            rf"^(?P<name>.+)-{re.escape(folder)}-"
            r"(?P<number>[a-z]{1,4}\d+[a-z]?|\d+[a-z]?)$",
            clean_stem,
            re.IGNORECASE,
        )

        if match:
            return {
                "set_id": folder,
                "card_number": match.group("number").upper(),
                "name": match.group("name"),
                "format": "name-folder-number",
            }

    # ---------------------------------------------------------
    # 11. Trainer-Kit
    # Beispiel: lucario-tk3l-03
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<name>.+)-(?P<set>tk\d+[a-z]?)-(?P<number>\d+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set").lower(),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "trainer-kit",
        }

    # ---------------------------------------------------------
    # 12. Box Topper
    # Beispiel: p08-box-topper-suicune
    # ---------------------------------------------------------
    match = re.match(
        r"^(?P<number>p\d+)-box-topper-(?P<name>.+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": "box-topper",
            "card_number": match.group("number").upper(),
            "name": match.group("name"),
            "format": "box-topper",
        }

    # ---------------------------------------------------------
    # 13. Miscellaneous
    # Beispiel: ancient-mew-1
    # ---------------------------------------------------------
    if folder == "miscellaneous":
        match = re.match(
            r"^(?:miscellaneous\.)?(?P<name>.+)-(?P<number>\d+)$",
            stem,
            re.IGNORECASE,
        )

        if match:
            return {
                "set_id": folder,
                "card_number": match.group("number"),
                "name": match.group("name"),
                "format": "miscellaneous",
            }

    # ---------------------------------------------------------
    # 14. Majestic Dawn
    # Beispiel: pachirisu43
    # ---------------------------------------------------------
    if folder == "majestic-dawn":
        match = re.match(
            r"^(?P<name>[a-z_-]+?)(?P<number>\d+)$",
            stem,
            re.IGNORECASE,
        )

        if match:
            return {
                "set_id": folder,
                "card_number": match.group("number"),
                "name": match.group("name"),
                "format": "name-number",
            }

    # ---------------------------------------------------------
    # 1. Black-Star-Promos
    #
    # Beispiele:
    # en_US-Promo_SWSH-SWSH240-finneon
    # en_US-Promo_SM-SM80-ho_oh_gx
    # en_US-Promo_XY-XY188-shaymin
    # en_US-Promo_BW-BW68-meloetta
    # ---------------------------------------------------------

    match = re.match(
        r"^en_US-Promo_(?P<era>SWSH|BW|XY|SM|SV)-"
        r"(?P<number>(?:SWSH|BW|XY|SM|SV)\d+)[_-](?P<name>.+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        promo_set_ids = {
            "BW": "bwbsp",
            "XY": "xybsp",
            "SM": "smbsp",
            "SWSH": "swshbsp",
            "SV": "svbsp",
        }

        return {
            "set_id": promo_set_ids[match.group("era").upper()],
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "en_US-promo-prefix-number-name",
        }

    # ---------------------------------------------------------
    # 2. Diamond-Pearl-Promos
    #
    # Beispiele:
    # giratina-lv.x-diamond-pearl-promos-dp38
    # magnezone-diamond-pearl-promos-dp32
    # ---------------------------------------------------------

    match = re.match(
        r"^(?P<name>.+)-diamond-pearl-promos-(?P<number>dp\d+)$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": "dpp",
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "name-diamond-pearl-promos-number",
        }

    # ---------------------------------------------------------
    # 3. en_US-XY7-001-oddish
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
    # 4. en_US-XY7-75a-hex_maniac-yaa
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
    # 5. en_US-SWSH10-TG001-abomasnow
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
    # 6. en_US-SF-SV085-grimmsnarl
    #     en_US-CZ-GG065-raihan
    #
    # Sondernummerierungen mit Buchstabenpräfix.
    # ---------------------------------------------------------

    match = re.match(
        r"^[a-z]{2}_[A-Z]{2}-(?P<set>[^-]+)-"
        r"(?P<number>[A-Za-z]{1,5}\d+)-(?P<name>.+)$",
        stem,
    )

    if match:
        return {
            "set_id": match.group("set"),
            "card_number": match.group("number"),
            "name": match.group("name"),
            "format": "en_US-set-prefixed-number-name",
        }

    # ---------------------------------------------------------
    # 7. sv3-5_en_001_std
    #    sv2_en_271
    #    sv1_en_050-1
    #
    # Optionales _std und zusätzliche Dateiendung -1.
    # ---------------------------------------------------------

    match = re.match(
        r"^(?P<set>.+)_en_(?P<number>\d+)(?:-\d+)?(?:_std)?$",
        stem,
        re.IGNORECASE,
    )

    if match:
        return {
            "set_id": match.group("set"),
            "card_number": match.group("number"),
            "name": "",
            "format": (
                "set-en-number-std"
                if stem.lower().endswith("_std")
                else "set-en-number"
            ),
        }

    # ---------------------------------------------------------
    # 8. name-set-code-number
    #
    # Beispiel:
    # aipom-aquapolis-aq-67
    # ---------------------------------------------------------

    match = re.match(
        r"^(?P<name>.+)-(?P<set_name>[a-z0-9]+)-"
        r"(?P<set_code>[a-z0-9]+)-(?P<number>\d+[a-z]?)"
        r"(?:-(?:normal|reverse|holo))?$",
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
    # 9. Expedition
    #
    # Beispiel:
    # h01-ampharos-expedition
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
