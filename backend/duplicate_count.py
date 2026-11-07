def calculate_iou(box1, box2):

    x1 = max(box1[0], box2[0])
    y1 = max(box1[1], box2[1])

    x2 = min(box1[2], box2[2])
    y2 = min(box1[3], box2[3])

    intersection = max(0, x2 - x1) * max(0, y2 - y1)

    area1 = (box1[2] - box1[0]) * (box1[3] - box1[1])
    area2 = (box2[2] - box2[0]) * (box2[3] - box2[1])

    union = area1 + area2 - intersection

    if union == 0:
        return 0

    return intersection / union


def remove_duplicates(detections, threshold=0.5):

    detections = sorted(
        detections,
        key=lambda x: x["confidence"],
        reverse=True
    )

    unique_objects = []

    for detection in detections:

        duplicate = False

        for existing in unique_objects:

            if detection["class_name"] == existing["class_name"]:

                iou = calculate_iou(
                    detection["bbox"],
                    existing["bbox"]
                )

                if iou > threshold:
                    duplicate = True
                    break

        if not duplicate:
            unique_objects.append(detection)

    return unique_objects


def count_objects(detections):

    counts = {}

    for detection in detections:
        name = detection["class_name"]
        counts[name] = counts.get(name, 0) + 1

    return counts


def detect_unique_objects(image_path):

    from backend.detect import detect_objects

    detections = detect_objects(image_path)

    unique_objects = remove_duplicates(detections)

    counts = count_objects(unique_objects)

    return {
        "total_unique_objects": len(unique_objects),
        "detected_objects": counts,
        "unique_detections": unique_objects
    }