import os
from xml.etree import ElementTree as ET
from PIL import Image
import zipfile

ROOT = os.getcwd()
ANNOTATIONS = os.path.join(ROOT, 'Annotations')
IMAGES_DIR = os.path.join(ROOT, 'images')
OUT_DIR = os.path.join(ROOT, 'defect_crops')
ZIP_NAME = os.path.join(ROOT, 'defect_crops.zip')


def parse_bboxes(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    boxes = []
    for i, obj in enumerate(root.findall('object')):
        name = obj.find('name').text if obj.find('name') is not None else 'obj'
        b = obj.find('bndbox')
        xmin = int(b.find('xmin').text)
        ymin = int(b.find('ymin').text)
        xmax = int(b.find('xmax').text)
        ymax = int(b.find('ymax').text)
        boxes.append((name, (xmin, ymin, xmax, ymax)))
    return boxes


def find_image(images_dir, folder, filename):
    candidates = [os.path.join(images_dir, folder, filename)]
    base, _ = os.path.splitext(filename)
    for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
        candidates.append(os.path.join(images_dir, folder, base + ext))
    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def ensure_dir(p):
    if not os.path.exists(p):
        os.makedirs(p, exist_ok=True)


def main():
    print('ROOT=', ROOT)
    print('ANNOTATIONS=', ANNOTATIONS)
    ensure_dir(OUT_DIR)
    xml_count = 0
    for _, _, files in os.walk(ANNOTATIONS):
        for f in files:
            if f.lower().endswith('.xml'):
                xml_count += 1
    print('XML files found in annotations:', xml_count)
    count = 0
    for root, dirs, files in os.walk(ANNOTATIONS):
        for f in files:
            if not f.lower().endswith('.xml'):
                continue
            xml_path = os.path.join(root, f)
            folder = os.path.basename(os.path.dirname(xml_path))
            try:
                tree = ET.parse(xml_path)
                r = tree.getroot()
                filename_tag = r.find('filename')
                if filename_tag is not None:
                    img_filename = filename_tag.text
                else:
                    img_filename = os.path.splitext(f)[0] + '.jpg'
            except Exception as e:
                print('Skip, parse fail:', xml_path, e)
                continue

            image_path = find_image(IMAGES_DIR, folder, img_filename)
            if image_path is None:
                print('Image not found for', xml_path)
                continue

            boxes = parse_bboxes(xml_path)
            if not boxes:
                continue

            img = Image.open(image_path).convert('RGB')
            iw, ih = img.size
            base = os.path.splitext(os.path.basename(image_path))[0]

            for idx, (cls, (xmin, ymin, xmax, ymax)) in enumerate(boxes, start=1):
                pad = int(max(2, 0.05 * max(xmax - xmin, ymax - ymin)))
                x0 = max(0, xmin - pad)
                y0 = max(0, ymin - pad)
                x1 = min(iw, xmax + pad)
                y1 = min(ih, ymax + pad)
                crop = img.crop((x0, y0, x1, y1))
                out_class_dir = os.path.join(OUT_DIR, cls)
                ensure_dir(out_class_dir)
                out_name = f"{base}_{idx}_{cls}.jpg"
                out_path = os.path.join(out_class_dir, out_name)
                crop.save(out_path)
                count += 1

    # create zip
    with zipfile.ZipFile(ZIP_NAME, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUT_DIR):
            for f in files:
                full = os.path.join(root, f)
                arcname = os.path.relpath(full, OUT_DIR)
                zf.write(full, arcname)

    print(f'Extracted {count} crops to {OUT_DIR} and zipped to {ZIP_NAME}')


if __name__ == '__main__':
    main()
