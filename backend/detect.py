from ultralytics import YOLO
from pathlib import Path

# Load the existing YOLO model
MODEL_PATH = Path(__file__).resolve().parent.parent / "yolo26n.pt"
model = YOLO(str(MODEL_PATH))


def detect_objects(image_path):
    results = model(image_path)

    counts = {}

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            class_name = model.names[class_id]

            counts[class_name] = counts.get(class_name, 0) + 1

    return counts