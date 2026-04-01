import json
from collections import Counter

with open('dataset_annotations.json','r',encoding='utf-8') as f:
    data = json.load(f)

total_objects = sum(len(v) for v in data.values())
unique_images = len(data)
per_class = Counter()
for objs in data.values():
    for o in objs:
        per_class[o['class']] += 1

print(f"total_objects:{total_objects}")
print(f"unique_images:{unique_images}")
for cls, cnt in per_class.items():
    print(f"class:{cls}:{cnt}")
