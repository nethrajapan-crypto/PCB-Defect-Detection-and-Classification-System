"""
Generate an HTML gallery for all PNG images found in the repository.
Saves `png_gallery.html` to the project root.
"""
import os
from pathlib import Path

ROOT = Path('.')
OUT_HTML = Path('png_gallery.html')

png_files = []
for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip hidden .venv and __pycache__
    if any(part.startswith('.') or part == '__pycache__' for part in Path(dirpath).parts):
        continue
    for f in filenames:
        if f.lower().endswith('.png'):
            full = Path(dirpath) / f
            # make path relative to ROOT for HTML
            rel = full.relative_to(ROOT)
            png_files.append(rel.as_posix())

png_files.sort()

html_parts = [
    '<!doctype html>',
    '<html lang="en">',
    '<head>',
    '  <meta charset="utf-8">',
    '  <meta name="viewport" content="width=device-width, initial-scale=1">',
    '  <title>PNG Gallery</title>',
    '  <style>',
    '    body{font-family:Segoe UI,Arial; padding:20px; background:#f7f7f7}',
    '    .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(300px,1fr));gap:16px}',
    '    .card{background:#fff;padding:10px;border-radius:8px;box-shadow:0 1px 4px rgba(0,0,0,0.08)}',
    '    img{max-width:100%;height:auto;border-radius:4px}',
    '    .caption{font-size:0.9rem;color:#333;margin-top:6px;word-break:break-all}',
    '  </style>',
    '</head>',
    '<body>',
    '  <h1>PNG Gallery</h1>',
    f'  <p>Total images: {len(png_files)}</p>',
    '  <div class="grid">'
]

for p in png_files:
    html_parts += [
        '    <div class="card">',
        f'      <a href="{p}" target="_blank"><img src="{p}" alt="{p}"></a>',
        f'      <div class="caption">{p}</div>',
        '    </div>'
    ]

html_parts += [
    '  </div>',
    '</body>',
    '</html>'
]

OUT_HTML.write_text('\n'.join(html_parts), encoding='utf-8')
print(f'PNG gallery created: {OUT_HTML} ({len(png_files)} images)')
