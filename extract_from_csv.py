import os
import csv
from PIL import Image
import zipfile

ROOT = os.getcwd()
CSV = os.path.join(ROOT, 'dataset_annotations.csv')
OUT_DIR = os.path.join(ROOT, 'defect_crops_csv')
ZIP_NAME = os.path.join(ROOT, 'defect_crops_csv.zip')


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)


def main():
    ensure_dir(OUT_DIR)
    count = 0
    with open(CSV, newline='', encoding='utf-8') as cf:
        reader = csv.DictReader(cf)
        for i, row in enumerate(reader, start=1):
            img_path = row['image']
            cls = row['class']
            xmin = int(row['xmin']); ymin = int(row['ymin']); xmax = int(row['xmax']); ymax = int(row['ymax'])
            if not os.path.exists(img_path):
                # try converting slashes
                img_path_alt = img_path.replace('/', os.sep).replace('\\', os.sep)
                if os.path.exists(img_path_alt):
                    img_path = img_path_alt
                else:
                    print('Missing image for row', i, img_path)
                    continue

            img = Image.open(img_path).convert('RGB')
            iw, ih = img.size
            pad = int(max(2, 0.05 * max(xmax - xmin, ymax - ymin)))
            x0 = max(0, xmin - pad); y0 = max(0, ymin - pad); x1 = min(iw, xmax + pad); y1 = min(ih, ymax + pad)
            crop = img.crop((x0, y0, x1, y1))
            base = os.path.splitext(os.path.basename(img_path))[0]
            out_class_dir = os.path.join(OUT_DIR, cls)
            ensure_dir(out_class_dir)
            out_name = f"{base}_{i}_{cls}.jpg"
            out_path = os.path.join(out_class_dir, out_name)
            crop.save(out_path)
            count += 1

    with zipfile.ZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUT_DIR):
            for f in files:
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, OUT_DIR)
                zf.write(full, arcname)

    print(f'Extracted {count} crops to {OUT_DIR} and zipped to {ZIP_NAME}')


if __name__ == '__main__':
    main()
