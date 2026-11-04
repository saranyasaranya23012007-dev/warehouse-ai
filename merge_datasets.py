
from pathlib import Path
import shutil

BASE = Path(__file__).resolve().parent
WAREHOUSE = BASE / "warehouse_recovered"
OUTPUT = BASE / "final_dataset"

# Warehouse original IDs -> final combined IDs
WAREHOUSE_MAP = {
    0: 10,  # forklift
    1: 11,  # person
}

def merge_warehouse(source, destination, prefix):
    images = source / "images"
    labels = source / "labels"

    if not images.is_dir() or not labels.is_dir():
        raise FileNotFoundError(
            f"Missing images or labels folder: {source}"
        )

    out_images = destination / "images"
    out_labels = destination / "labels"
    out_images.mkdir(parents=True, exist_ok=True)
    out_labels.mkdir(parents=True, exist_ok=True)

    count = 0

    for image in sorted(images.iterdir()):
        if not image.is_file() or image.suffix.lower() not in (
            ".jpg", ".jpeg", ".png", ".bmp", ".webp"
        ):
            continue

        label = labels / (image.stem + ".txt")
        if not label.is_file():
            raise FileNotFoundError(f"Label missing: {label}")

        new_image = out_images / f"{prefix}_{image.name}"
        new_label = out_labels / f"{prefix}_{image.stem}.txt"

        # Do not overwrite existing files.
        if new_image.exists() or new_label.exists():
            print("Already exists, skipping:", image.name)
            continue

        converted = []
        for line_no, line in enumerate(
            label.read_text(encoding="utf-8").splitlines(), 1
        ):
            parts = line.split()
            if not parts:
                continue

            if len(parts) != 5:
                raise ValueError(f"Invalid label: {label}, line {line_no}")

            old_id = int(parts[0])
            if old_id not in WAREHOUSE_MAP:
                raise ValueError(f"Unknown class {old_id}: {label}")

            coords = [float(v) for v in parts[1:]]
            if not all(0 <= v <= 1 for v in coords):
                raise ValueError(f"Invalid normalized coordinates: {label}")

            converted.append(
                f"{WAREHOUSE_MAP[old_id]} " +
                " ".join(f"{v:.6f}" for v in coords)
            )

        # Copy image and write remapped labels.
        shutil.copy2(image, new_image)
        new_label.write_text(
            "\n".join(converted) + ("\n" if converted else ""),
            encoding="utf-8"
        )
        count += 1

    print(f"{prefix}: {count} new images merged")

def main():
    if not OUTPUT.is_dir():
        raise FileNotFoundError(
            f"Existing final_dataset folder not found: {OUTPUT}"
        )

    # Preserve the lab files already in final_dataset.
    merge_warehouse(
        WAREHOUSE / "train",
        OUTPUT / "train",
        "warehouse_train"
    )

    merge_warehouse(
        WAREHOUSE / "validation",
        OUTPUT / "val",
        "warehouse_val"
    )

    print("\nWarehouse merge finished.")
    print("Existing lab dataset files were preserved.")

if __name__ == "__main__":
    main()
