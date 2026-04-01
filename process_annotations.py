"""Process all Pascal VOC XML annotations, draw boxes on images,
and produce a CSV and JSON summary of defects.

Usage:
  python process_annotations.py
Optional args: --annotations, --images, --out-csv, --out-json, --no-annotate
"""
import os
import json
import csv
import argparse
from xml.etree import ElementTree as ET
from show_missing_hole import draw_boxes, parse_bboxes


def find_image(images_dir, folder, filename):
    # Try the common locations and extensions
    candidates = []
    candidates.append(os.path.join(images_dir, folder, filename))
    base, _ = os.path.splitext(filename)
    for ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff']:
        candidates.append(os.path.join(images_dir, folder, base + ext))

    for p in candidates:
        if os.path.exists(p):
            return p
    return None


def process(annotations_dir, images_dir, out_csv, out_json, annotate=True):
    rows = []
    summary = {}

    for root, dirs, files in os.walk(annotations_dir):
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
                print('Failed to parse', xml_path, '->', e)
                continue

            image_path = find_image(images_dir, folder, img_filename)
            if image_path is None:
                print('Image not found for', xml_path, 'expected', img_filename)
                continue

            # parse boxes using helper
            try:
                boxes = parse_bboxes(xml_path)
            except Exception as e:
                print('Failed to parse bboxes for', xml_path, '->', e)
                continue

            rel_image = os.path.relpath(image_path, os.getcwd())
            summary.setdefault(rel_image, [])

            for name, (xmin, ymin, xmax, ymax) in boxes:
                rows.append({
                    'image': rel_image,
                    'class': name,
                    'xmin': xmin,
                    'ymin': ymin,
                    'xmax': xmax,
                    'ymax': ymax,
                })
                summary[rel_image].append({'class': name, 'bbox': [xmin, ymin, xmax, ymax]})

            if annotate:
                # save annotated image next to original
                base, ext = os.path.splitext(image_path)
                out_path = base + '_annotated' + ext
                try:
                    draw_boxes(image_path, xml_path, out_path)
                except Exception as e:
                    print('Failed to annotate', image_path, '->', e)

    # write CSV
    with open(out_csv, 'w', newline='', encoding='utf-8') as cf:
        writer = csv.DictWriter(cf, fieldnames=['image', 'class', 'xmin', 'ymin', 'xmax', 'ymax'])
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # write JSON
    with open(out_json, 'w', encoding='utf-8') as jf:
        json.dump(summary, jf, indent=2)

    print('Wrote', out_csv, 'and', out_json)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--annotations', default='Annotations', help='Annotations directory')
    p.add_argument('--images', default='images', help='Images directory')
    p.add_argument('--out-csv', default='dataset_annotations.csv', help='CSV output')
    p.add_argument('--out-json', default='dataset_annotations.json', help='JSON output')
    p.add_argument('--no-annotate', action='store_true', help='Do not write annotated images')
    args = p.parse_args()

    process(args.annotations, args.images, args.out_csv, args.out_json, annotate=not args.no_annotate)


if __name__ == '__main__':
    main()
