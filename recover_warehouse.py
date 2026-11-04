import os
import requests
import pandas as pd
from io import BytesIO
from PIL import Image

BASE = "https://huggingface.co/datasets/keremberke/forklift-object-detection/resolve/refs%2Fconvert%2Fparquet/full"
OUT = "warehouse_recovered"

for split in ["train", "validation"]:
    print("\nProcessing:", split)

    url = f"{BASE}/{split}/0000.parquet"
    response = requests.get(url, timeout=180)
    response.raise_for_status()
    df = pd.read_parquet(BytesIO(response.content))

    image_dir = os.path.join(OUT, split, "images")
    label_dir = os.path.join(OUT, split, "labels")
    os.makedirs(image_dir, exist_ok=True)
    os.makedirs(label_dir, exist_ok=True)

    for i, row in df.iterrows():
        image_data = row["image"]
        objects = row["objects"]

        if isinstance(image_data, dict):
            image_data = image_data.get("bytes")

        if not image_data:
            print("Skipping image without bytes:", i)
            continue

        image = Image.open(BytesIO(image_data)).convert("RGB")
        width, height = image.size

        name = f"{split}_{i:04d}"
        image.save(os.path.join(image_dir, name + ".jpg"))

        lines = []
        if isinstance(objects, dict):
            boxes = objects.get("bbox", [])
            categories = objects.get("category", [])
        else:
            boxes = []
            categories = []

        for box, category in zip(boxes, categories):
            if isinstance(box, dict):
                x = box.get("xmin", box.get("x", 0))
                y = box.get("ymin", box.get("y", 0))
                w = box.get("xmax", x) - x
                h = box.get("ymax", y) - y
            else:
                if len(box) != 4:
                    continue
                x, y, w, h = box

            # Skip invalid bounding boxes
            if w <= 0 or h <= 0:
                continue

            # Convert pixel coordinates to YOLO normalized format
            xc = (x + w / 2) / width
            yc = (y + h / 2) / height
            nw = w / width
            nh = h / height

            # Dataset category 0 = forklift, 1 = person
            try:
                class_id = int(category)
            except (TypeError, ValueError):
                continue

            if class_id not in (0, 1):
                continue

            lines.append(
                f"{class_id} {xc:.6f} {yc:.6f} {nw:.6f} {nh:.6f}"
            )

        with open(os.path.join(label_dir, name + ".txt"), "w") as f:
            f.write("\n".join(lines))

        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(df)} images")

    print("Finished:", split)

print("\nWarehouse export finished.")