from pathlib import Path
import json
import time
import requests


OUTPUT_DIR = Path("data/official_metadata")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SETS_URL = (
    "https://raw.githubusercontent.com/"
    "PokemonTCG/pokemon-tcg-data/master/sets/en.json"
)

CARDS_BASE_URL = (
    "https://raw.githubusercontent.com/"
    "PokemonTCG/pokemon-tcg-data/master/cards/en"
)


def download_json(url, output_file):
    print(f"  Lade: {url}")

    response = requests.get(url, timeout=30)
    response.raise_for_status()

    data = response.json()

    with output_file.open("w", encoding="utf-8") as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
        )

    return data


def main():
    print("=" * 60)
    print("OFFIZIELLE POKÉMON-TCG-METADATEN")
    print("=" * 60)

    sets_file = OUTPUT_DIR / "sets.json"

    # ---------------------------------------------------------
    # 1. Set-Liste herunterladen
    # ---------------------------------------------------------

    if sets_file.exists():
        print("\nSet-Daten bereits vorhanden.")
        with sets_file.open("r", encoding="utf-8") as f:
            sets = json.load(f)
    else:
        print("\nLade offizielle Set-Liste...")
        sets = download_json(SETS_URL, sets_file)

    print(f"Sets gefunden: {len(sets)}")

    # ---------------------------------------------------------
    # 2. Kartendaten aller Sets herunterladen
    # ---------------------------------------------------------

    cards_dir = OUTPUT_DIR / "cards"
    cards_dir.mkdir(exist_ok=True)

    downloaded = 0
    skipped = 0
    failed = []

    for index, pokemon_set in enumerate(sets, start=1):
        set_id = pokemon_set["id"]
        set_name = pokemon_set["name"]

        output_file = cards_dir / f"{set_id}.json"

        print(
            f"\n[{index}/{len(sets)}] "
            f"{set_id} - {set_name}"
        )

        if output_file.exists():
            print("  bereits vorhanden")
            skipped += 1
            continue

        url = f"{CARDS_BASE_URL}/{set_id}.json"

        try:
            download_json(url, output_file)
            downloaded += 1

            # GitHub nicht unnötig schnell anfragen
            time.sleep(0.15)

        except Exception as e:
            print(f"  FEHLER: {e}")
            failed.append(set_id)

    print("\n" + "=" * 60)
    print("FERTIG")
    print("=" * 60)

    print(f"Sets insgesamt:       {len(sets)}")
    print(f"Neu heruntergeladen:  {downloaded}")
    print(f"Bereits vorhanden:    {skipped}")
    print(f"Fehlgeschlagen:        {len(failed)}")

    if failed:
        print("\nFehlgeschlagene Sets:")
        for set_id in failed:
            print(f"  {set_id}")

    print("\nGespeichert unter:")
    print(OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()