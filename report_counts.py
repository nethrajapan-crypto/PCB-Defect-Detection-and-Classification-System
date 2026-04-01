import csv
import os

csv_path = 'dataset_annotations.csv'
if not os.path.exists(csv_path):
    print('dataset_annotations.csv not found')
    raise SystemExit(1)

total = 0
classes = {}
images = set()
with open(csv_path, newline='', encoding='utf-8') as f:
    r = csv.DictReader(f)
    for row in r:
        total += 1
        classes[row['class']] = classes.get(row['class'], 0) + 1
        images.add(row['image'])

print('Total defects:', total)
print('Unique images with annotations:', len(images))
print('Per-class counts:')
for k in sorted(classes, key=lambda x: classes[x], reverse=True):
    print(f'  {k}: {classes[k]}')

print('\nFiles:')
for fn in ['annotated_images.zip','defect_crops.zip','defect_crops_csv.zip','dataset_annotations.csv','dataset_annotations.json','gallery.html']:
    print(f'  {fn}:', os.path.exists(fn) and os.path.getsize(fn) or 'MISSING')
