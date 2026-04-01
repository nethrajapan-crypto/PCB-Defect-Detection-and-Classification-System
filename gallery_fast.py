#!/usr/bin/env python3
"""Build interactive defect gallery from dataset_annotations.json"""

import json
import os

IN_JSON = "dataset_annotations.json"
OUT_HTML = "defect_gallery_annotated.html"

COLORS = {
    "missing_hole": "#FF6B6B",
    "mouse_bite": "#4ECDC4",
    "open_circuit": "#FFE66D",
    "short": "#95E1D3",
    "spur": "#C7CEEA",
    "spurious_copper": "#FF8B94"
}

def main():
    if not os.path.exists(IN_JSON):
        print(f"Missing {IN_JSON}")
        return

    with open(IN_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)

    classes = sorted(set(obj["class"] for objs in data.values() for obj in objs))
    
    # Group images by class with defect counts
    by_class = {c: {} for c in classes}
    total_defects = 0
    
    for img_path, objs in data.items():
        for obj in objs:
            cls = obj["class"]
            if img_path not in by_class[cls]:
                by_class[cls][img_path] = 0
            by_class[cls][img_path] += 1
            total_defects += 1

    total_images = len(data)
    total_classes = len(classes)

    html = """
<html>
<head>
<meta charset="utf-8">
<title>PCB Defect Gallery</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f0f2f5; padding: 20px; }
.container { max-width: 1400px; margin: 0 auto; }
.header { background: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
h1 { color: #333; margin-bottom: 15px; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 15px; margin: 20px 0; }
.stat-box { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 6px; }
.stat-num { font-size: 28px; font-weight: bold; }
.stat-label { font-size: 14px; opacity: 0.9; margin-top: 5px; }
.filter-section { background: white; padding: 20px; border-radius: 8px; margin-bottom: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
.filter-label { font-weight: bold; margin-bottom: 10px; color: #333; }
.filter-buttons { display: flex; flex-wrap: wrap; gap: 8px; }
.btn { padding: 10px 18px; border: 2px solid #ddd; background: white; border-radius: 20px; cursor: pointer; font-size: 14px; font-weight: 500; transition: all 0.2s; }
.btn:hover { background: #f5f5f5; border-color: #999; }
.btn.active { color: white; border-color: #667eea; background: #667eea; }
.gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 15px; margin-top: 20px; }
.card { background: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); transition: transform 0.2s, box-shadow 0.2s; cursor: pointer; }
.card:hover { transform: translateY(-4px); box-shadow: 0 4px 16px rgba(0,0,0,0.15); }
.card-img { width: 100%; height: 280px; object-fit: cover; background: #f0f0f0; }
.card-info { padding: 15px; }
.card-title { font-size: 14px; color: #555; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-bottom: 8px; }
.card-meta { display: flex; align-items: center; justify-content: space-between; }
.badge { display: inline-block; padding: 6px 12px; border-radius: 20px; color: white; font-size: 12px; font-weight: 600; }
.defect-count { background: #999; color: white; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; }
.modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); z-index: 1000; align-items: center; justify-content: center; }
.modal.show { display: flex; }
.modal-content { background: white; border-radius: 8px; max-width: 90vw; max-height: 90vh; overflow: auto; position: relative; }
.modal-img { width: 100%; height: auto; display: block; }
.close-modal { position: absolute; top: 10px; right: 15px; background: rgba(0,0,0,0.5); color: white; border: none; font-size: 24px; cursor: pointer; padding: 5px 10px; border-radius: 4px; }
.close-modal:hover { background: rgba(0,0,0,0.8); }
</style>
<script>
function filterClass(cls) {
  var btns = document.querySelectorAll('.filter-buttons .btn');
  btns.forEach(b => b.classList.remove('active'));
  event.target.classList.add('active');
  
  var cards = document.querySelectorAll('.card');
  cards.forEach(c => {
    if (cls === 'all' || c.dataset.class === cls) {
      c.style.display = 'block';
    } else {
      c.style.display = 'none';
    }
  });
}

function openModal(src) {
  var modal = document.getElementById('modal');
  var img = document.getElementById('modal-img');
  img.src = src;
  modal.classList.add('show');
}

function closeModal() {
  document.getElementById('modal').classList.remove('show');
}

window.onclick = function(e) {
  var modal = document.getElementById('modal');
  if (e.target === modal) {
    closeModal();
  }
}
</script>
</head>
<body>
<div class="container">
<div class="header">
<h1>PCB Defect Detection Gallery</h1>
<p style="color: #666; margin-top: 8px;">All detected defects with class filtering</p>

<div class="stats">
<div class="stat-box">
  <div class="stat-num">""" + str(total_images) + """</div>
  <div class="stat-label">Total Images Analyzed</div>
</div>
<div class="stat-box" style="background: linear-gradient(135deg, #56ab2f 0%, #a8e063 100%);">
  <div class="stat-num">""" + str(total_defects) + """</div>
  <div class="stat-label">Total Defects Detected</div>
</div>
<div class="stat-box" style="background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); color: #333;">
  <div class="stat-num">""" + str(total_classes) + """</div>
  <div class="stat-label">Defect Classes</div>
</div>
</div>
</div>

<div class="filter-section">
<div class="filter-label">Filter by Defect Type:</div>
<div class="filter-buttons">
<button class="btn active" onclick="filterClass('all')">All Classes (""" + str(sum(len(by_class[c]) for c in classes)) + """)</button>
"""

    # Add class buttons
    for cls in classes:
        count = len(by_class[cls])
        color = COLORS.get(cls, "#ccc")
        html += f'<button class="btn" onclick="filterClass(\'{cls}\')" style="border-color: {color}; color: {color};">{cls.replace("_", " ").title()} ({count})</button>\n'

    html += """
</div>
</div>

<div class="gallery">
"""

    # Add cards
    for cls in classes:
        for img_path in sorted(by_class[cls].keys()):
            defect_count = by_class[cls][img_path]
            img_display = img_path.replace('\\', '/').split('/')[-1]
            img_url = img_path.replace('\\', '/')
            color = COLORS.get(cls, "#ccc")
            
            html += f"""<div class="card" data-class="{cls}" onclick="openModal('{img_url}')">
  <img class="card-img" src="{img_url}" alt="{img_display}" loading="lazy">
  <div class="card-info">
    <div class="card-title">{img_display}</div>
    <div class="card-meta">
      <span class="badge" style="background: {color};">{cls.replace("_", " ").title()}</span>
      <span class="defect-count">{defect_count}</span>
    </div>
  </div>
</div>
"""

    html += """
</div>
</div>

<div id="modal" class="modal">
  <div class="modal-content">
    <button class="close-modal" onclick="closeModal()">&times;</button>
    <img id="modal-img" class="modal-img" src="" alt="">
  </div>
</div>

</body>
</html>
"""

    with open(OUT_HTML, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ Created {OUT_HTML}")
    print(f"  Images: {total_images} | Defects: {total_defects} | Classes: {total_classes}")

if __name__ == '__main__':
    main()
