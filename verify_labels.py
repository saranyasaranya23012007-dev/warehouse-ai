
from pathlib import Path
from collections import Counter

base = Path("final_dataset")
counts = Counter()
bad = []
total_boxes = 0

for split in ["train", "val"]:
    label_dir = base / split / "labels"

    for file in label_dir.glob("*.txt"):
        for line_num, line in enumerate(
            file.read_text(encoding="utf-8").splitlines(), 1
        ):
            parts = line.split()

            if len(parts) != 5:
                bad.append((str(file), line_num, "wrong number of values"))
                continue

            try:
                class_id = int(parts[0])
                coords = [float(x) for x in parts[1:]]
            except ValueError:
                bad.append((str(file), line_num, "invalid number"))
                continue

            total_boxes += 1
            counts[class_id] += 1

            if not 0 <= class_id <= 11:
                bad.append((str(file), line_num, "class ID outside 0-11"))

            if any(not 0 <= x <= 1 for x in coords):
                bad.append((str(file), line_num, "coordinate outside 0-1"))

print("Class counts:", dict(sorted(counts.items())))
print("Total boxes:", total_boxes)
print("Invalid rows:", len(bad))
print("Examples:", bad[:5])
