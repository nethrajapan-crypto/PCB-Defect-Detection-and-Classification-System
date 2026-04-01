import json
from collections import Counter

PATH = "dataset_annotations.json"

def main():
    with open(PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    class_counter = Counter()
    total_objects = 0
    for img, objs in data.items():
        for o in objs:
            cls = o.get("class")
            class_counter[cls] += 1
            total_objects += 1

    summary = {
        "total_images": len(data),
        "total_objects": total_objects,
        "per_class": dict(class_counter)
    }

    print(json.dumps(summary, indent=2))

if __name__ == "__main__":
    main()
