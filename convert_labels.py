
from pathlib import Path
import shutil

base = Path("final_dataset")
backup = Path("final_dataset_labels_backup")

if not backup.exists():
    shutil.copytree(
        base,
        backup,
        ignore=shutil.ignore_patterns("images", "*.jpg", "*.jpeg", "*.png", "*.webp")
    )

converted = 0
already_boxes = 0
bad = []

for split in ["train", "val"]:
    label_dir = base / split / "labels"

    for file in label_dir.glob("*.txt"):
        output = []

        for line_no, line in enumerate(
            file.read_text(encoding="utf-8").splitlines(), 1
        ):
            parts = line.split()
            if not parts:
                continue

            try:
                cls = int(parts[0])
                coords = [float(v) for v in parts[1:]]
            except ValueError:
                bad.append((str(file), line_no, "invalid number"))
                continue

            if len(coords) == 4:
                cx, cy, w, h = coords
                already_boxes += 1

            elif len(coords) >= 6 and len(coords) % 2 == 0:
                xs = coords[0::2]
                ys = coords[1::2]

                if any(v < 0 or v > 1 for v in coords):
                    bad.append((str(file), line_no, "polygon coordinate outside 0-1"))
                    continue

                xmin, xmax = min(xs), max(xs)
                ymin, ymax = min(ys), max(ys)
                cx = (xmin + xmax) / 2
                cy = (ymin + ymax) / 2
                w = xmax - xmin
                h = ymax - ymin
                converted += 1

            else:
                bad.append((str(file), line_no, "unexpected coordinate count"))
                continue

            if not (0 <= cx <= 1 and 0 <= cy <= 1
                    and 0 < w <= 1 and 0 < h <= 1):
                bad.append((str(file), line_no, "invalid bounding box"))
                continue

            output.append(
                f"{cls} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"
            )

        file.write_text(
            "\n".join(output) + ("\n" if output else ""),
            encoding="utf-8"
        )

print("Polygon labels converted:", converted)
print("Existing box labels:", already_boxes)
print("Invalid lines:", len(bad))
print("Examples:", bad[:10])
print("Backup folder:", backup)
