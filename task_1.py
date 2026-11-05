"""Task 1: recursively copy and group files by extension."""

import argparse
import shutil
import sys
from pathlib import Path


def unique_destination(directory: Path, filename: str) -> Path:
    """Find an unused filename to avoid overwriting existing files."""
    candidate = directory / filename
    if not candidate.exists():
        return candidate

    original = Path(filename)
    index = 1
    while True:
        candidate = directory / f"{original.stem}_{index}{original.suffix}"
        if not candidate.exists():
            return candidate
        index += 1


def copy_recursive(source: Path, destination: Path, stats: dict[str, int]) -> None:
    """Recursively visit source and copy files into extension directories."""
    try:
        entries = sorted(source.iterdir(), key=lambda item: item.name.casefold())
    except OSError as error:
        print(f"Не вдалося прочитати {source}: {error}", file=sys.stderr)
        stats["errors"] += 1
        return

    for entry in entries:
        if entry == destination:
            continue  # The destination may be inside the source tree.

        try:
            if entry.is_symlink():
                print(f"Пропущено символічне посилання: {entry}")
                continue

            if entry.is_dir():
                copy_recursive(entry, destination, stats)
            elif entry.is_file():
                extension = entry.suffix.lower().lstrip(".") or "no_extension"
                target_directory = destination / extension
                target_directory.mkdir(parents=True, exist_ok=True)
                target_path = unique_destination(target_directory, entry.name)
                shutil.copy2(entry, target_path)
                stats["copied"] += 1
                print(f"Скопійовано: {entry} -> {target_path}")
        except OSError as error:
            print(f"Не вдалося обробити {entry}: {error}", file=sys.stderr)
            stats["errors"] += 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Рекурсивно копіює файли та сортує їх за розширеннями."
    )
    parser.add_argument("source", type=Path, help="Вихідна директорія")
    parser.add_argument(
        "destination", nargs="?", type=Path, default=Path("dist"),
        help="Директорія призначення (за замовчуванням: ./dist)",
    )
    args = parser.parse_args()

    source = args.source.resolve()
    destination = args.destination.resolve()

    if not source.is_dir():
        print(f"Помилка: вихідної директорії не існує: {source}", file=sys.stderr)
        return 1
    if source == destination:
        print("Помилка: директорії джерела і призначення збігаються.", file=sys.stderr)
        return 1

    try:
        destination.mkdir(parents=True, exist_ok=True)
    except OSError as error:
        print(f"Не вдалося створити директорію призначення: {error}", file=sys.stderr)
        return 1

    stats = {"copied": 0, "errors": 0}
    copy_recursive(source, destination, stats)
    print(f"Завершено. Скопійовано: {stats['copied']}; помилок: {stats['errors']}.")
    return 1 if stats["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
