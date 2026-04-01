import json
import os

ROOT = os.getcwd()
JSON_PATH = os.path.join(ROOT, 'dataset_annotations.json')
OUT_HTML = os.path.join(ROOT, 'gallery.html')


def build():
    with open(JSON_PATH, 'r', encoding='utf-8') as f:
        annotations = json.load(f)

    # produce HTML with embedded JSON
    json_text = json.dumps(annotations)
    html = '''<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <title>Annotated Images Gallery</title>
  <style>
    body { font-family: Arial, sans-serif; margin:0; }
    #sidebar { width:280px; height:100vh; overflow:auto; border-right:1px solid #ddd; float:left; padding:10px; box-sizing:border-box }
    #main { margin-left:280px; padding:10px }
    .thumb { width:100%; margin-bottom:8px; cursor:pointer; border:1px solid #ccc }
    #canvasWrap { position:relative; display:inline-block }
    #imgCanvas { border:1px solid #333; }
    .bboxInfo { font-size:13px; margin:6px 0 }
  </style>
</head>
<body>
  <div id="sidebar">
    <h3>Images</h3>
    <div id="list"></div>
  </div>
  <div id="main">
    <h2 id="title">Select an image</h2>
    <div id="canvasWrap">
      <canvas id="imgCanvas"></canvas>
    </div>
    <div id="info"></div>
  </div>

  <script>
    const annotations = ''' + json_text + ''';

    const listEl = document.getElementById('list');
    const titleEl = document.getElementById('title');
    const infoEl = document.getElementById('info');
    const canvas = document.getElementById('imgCanvas');
    const ctx = canvas.getContext('2d');

    const images = Object.keys(annotations).sort();
    function relToAbs(p){ return p.replace(/\\/g,'/'); }

    images.forEach(im => {
      const div = document.createElement('div');
      const img = document.createElement('img');
      img.src = relToAbs(im);
      img.className = 'thumb';
      img.onload = ()=>{ if (img.naturalWidth>260) img.width = 260 }
      img.onclick = ()=> loadImage(im);
      div.appendChild(img);
      listEl.appendChild(div);
    });

    function loadImage(im){
      const img = new Image();
      img.onload = ()=>{
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.clearRect(0,0,canvas.width,canvas.height);
        ctx.drawImage(img,0,0);
        // draw boxes
        const anns = annotations[im] || [];
        infoEl.innerHTML = '';
        anns.forEach(a=>{
          const [xmin,ymin,xmax,ymax] = a.bbox;
          ctx.strokeStyle = 'red'; ctx.lineWidth = Math.max(2, Math.round(canvas.width/600));
          ctx.strokeRect(xmin, ymin, xmax-xmin, ymax-ymin);
          ctx.fillStyle = 'red'; ctx.font = '14px Arial';
          ctx.fillRect(xmin, Math.max(0,ymin-18), ctx.measureText(a.class).width+8, 18);
          ctx.fillStyle='white'; ctx.fillText(a.class, xmin+4, Math.max(0,ymin-4));

          const info = document.createElement('div'); info.className='bboxInfo';
          info.textContent = `${a.class}: [${a.bbox.join(', ')}]`;
          infoEl.appendChild(info);
        });
        titleEl.textContent = im;
      };
      img.src = relToAbs(im);
    }

    // auto-load first image if present
    if (images.length) loadImage(images[0]);
  </script>
</body>
</html>
'''

    with open(OUT_HTML, 'w', encoding='utf-8') as o:
        o.write(html)
    print('Wrote', OUT_HTML)


if __name__ == '__main__':
    build()
