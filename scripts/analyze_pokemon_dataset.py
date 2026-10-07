from pathlib import Path
from collections import Counter
from PIL import Image
import hashlib


DATASET_DIR = Path(r"C:\Users\sylwi\Documents\PokemonData\Pokemon TCG\Pokemon TCG")


def file_hash(path: Path) -> str:
    """Berechnet einen Hash des Bildinhalts."""
    h = hashlib.md5()

    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)

    return h.hexdigest()


def main():
    print("=" * 60)
    print("POKÉMON-DATENSATZ ANALYSE")
    print("=" * 60)

    if not DATASET_DIR.exists():
        print(f"\nFEHLER: Datensatz nicht gefunden:")
        print(DATASET_DIR)
        return

    extensions = {".jpg", ".jpeg", ".png", ".webp"}

    files = [
        p for p in DATASET_DIR.rglob("*")
        if p.is_file() and p.suffix.lower() in extensions
    ]

    print(f"\nDatensatz:")
    print(DATASET_DIR)

    print(f"\nGesamtzahl Bilder: {len(files)}")

    # Dateiformate
    extension_counts = Counter(
        p.suffix.lower()
        for p in files
    )

    print("\nDateiformate:")
    for ext, count in sorted(extension_counts.items()):
        print(f"  {ext}: {count}")

    # Ordnerverteilung
    folder_counts = Counter(
        p.parent.relative_to(DATASET_DIR).parts[0]
        if p.parent != DATASET_DIR
        else "(Hauptordner)"
        for p in files
    )

    print("\nBilder pro oberstem Ordner:")
    for folder, count in sorted(folder_counts.items()):
        print(f"  {folder}: {count}")

    # Bildprüfung
    print("\nPrüfe Bilder ...")

    broken = []
    dimensions = Counter()

    for i, path in enumerate(files, start=1):
        try:
            with Image.open(path) as img:
                img.verify()

            with Image.open(path) as img:
                dimensions[img.size] += 1

        except Exception as e:
            broken.append((path, str(e)))

        if i % 1000 == 0 or i == len(files):
            print(f"  {i}/{len(files)}")

    print("\nBildprüfung:")
    print(f"  Lesbar: {len(files) - len(broken)}")
    print(f"  Fehler: {len(broken)}")

    # Bildgrößen
    print("\nBildgrößen:")
    for size, count in dimensions.most_common():
        print(f"  {size[0]} x {size[1]}: {count}")

    # Duplikate über Dateiinhalt
    print("\nSuche nach identischen Bildinhalten ...")

    hashes = {}
    duplicates = []

    for i, path in enumerate(files, start=1):
        try:
            h = file_hash(path)

            if h in hashes:
                duplicates.append((path, hashes[h]))
            else:
                hashes[h] = path

        except Exception:
            pass

        if i % 1000 == 0 or i == len(files):
            print(f"  {i}/{len(files)}")

    print(f"\nIdentische Duplikate: {len(duplicates)}")

    if duplicates:
        print("\nBeispiele:")
        for duplicate, original in duplicates[:20]:
            print(f"  {duplicate}")
            print(f"    = {original}")

    # Fehlerhafte Dateien
    if broken:
        print("\nFehlerhafte Dateien:")

        for path, error in broken[:20]:
            print(f"  {path}")
            print(f"    {error}")

    print("\n" + "=" * 60)
    print("ANALYSE FERTIG")
    print("=" * 60)


if __name__ == "__main__":
    main()