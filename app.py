import csv
import datetime
import os
from flask import Flask, request, redirect, url_for, render_template_string, send_from_directory
from werkzeug.utils import secure_filename

from predict_and_annotate import load_model, annotate_image, predict_image, compute_subtraction
from compute_confusion_matrices import main as compute_confusion

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from io import BytesIO

UPLOAD_FOLDER = 'uploaded'
OUTPUT_FOLDER = 'web_output'
HISTORY_CSV = 'history.csv'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app = Flask(__name__, static_folder='static', static_url_path='/static')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['OUTPUT_FOLDER'] = OUTPUT_FOLDER

# Global variables for last detection results
last_original_path = None
last_subtraction_path = None
last_annotated_path = None
last_pred_class = None
last_defect_type = None
last_confidence = None
last_template_name = None
last_test_name = None

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs('static', exist_ok=True)
os.makedirs('analysis', exist_ok=True)

if not os.path.exists(HISTORY_CSV):
    with open(HISTORY_CSV, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['timestamp', 'template_file', 'test_file', 'pred_class', 'defect_type', 'confidence', 'annotated_file'])


def detect_defect_type(filename):
    name = filename.lower()
    if 'missing_hole' in name or 'missing-hole' in name or 'hole_missing' in name:
        return 'missing_hole'
    if 'mouse_bite' in name or 'mouse-bite' in name:
        return 'mouse_bite'
    if 'open_circuit' in name or 'open-circuit' in name or 'open_circ' in name:
        return 'open_circuit'
    if 'short' in name:
        return 'short'
    if 'spur' in name:
        return 'spur'
    if 'spurious' in name or 'spurious_copper' in name:
        return 'spurious_copper'
    return 'unknown'


HTML_TEMPLATE = '''
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>VISIONCORE AI REPORT - PCB Defect Detection</title>
  <style>
    body { margin:0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#070d19; color:#e5e9ee; }
    .bar { background:#141f2e; border-bottom:1px solid #2e3c4f; display:flex; justify-content:space-between; align-items:center; padding:14px 24px; }
    .bar h1 { margin:0; color:#49dcff; font-size:1.85rem; }
    .bar .action { display:flex; align-items:center; gap:10px; }
    .action a { color:#ffffff; background:#1d7cd8; padding:9px 14px; border-radius:8px; text-decoration:none; font-weight:600; }
    .action a:hover { background:#2a93ff; }
    .container { padding:20px; }
    .card { background:#101d30; border:1px solid #2d3e53; border-radius:10px; padding:15px; margin-bottom:18px; }
    .card h2 { margin:0 0 8px; color:#87d8ff; }
    .upload-area { border:2px dashed #3f5d86; padding:14px; border-radius:9px; text-align:center; background:#131f31; }
    .upload-area p { margin:8px 0; }
    .grid2 { display:grid; grid-template-columns:repeat(2,minmax(0,1fr)); gap:13px; }
    .output-img { width:100%; border-radius:8px; border:1px solid #2f445f; }
    .status { margin-top:10px; padding:10px; border-radius:8px; background:#12263b; border:1px solid #2c3d54; }
    .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(180px,1fr)); gap:10px; margin-top:10px; }
    .chip { border:1px solid #2f4561; border-radius:8px; padding:9px; background:#122437; }
    .chip strong { color:#a5d6ff; }
    .history-table { width:100%; border-collapse:collapse; }
    .history-table th, .history-table td { border:1px solid #2f4055; padding:8px; font-size:0.86rem; }
    .history-table th { background:#1f2f45; text-align:left; }
    .subtraction-img {
      width: 100%;
      height: auto;
      max-width: 300px;
      max-height: 300px;
      background-color: black;
      border: 3px solid #ffcc00;
      border-radius: 10px;
      display: block;
      margin: 0 auto;
      padding: 10px;
    }
  </style>
</head>
<body>
  <div class="bar">
    <h1>VISIONCORE AI REPORT</h1>
    <div class="action">
      <a href="/download-report">Download Report PDF</a>
      <a href="/history">View History</a>
    </div>
  </div>

  <div class="container">
    <div class="card">
      <h2>1. Upload PCB (Template + Test)</h2>
      <form method="post" enctype="multipart/form-data">
        <div class="grid2">
          <div class="upload-area">
            <p><strong>Template PCB Image</strong></p>
            <input type="file" name="template_file" accept="image/png,image/jpeg,image/jpg,image/bmp" required>
          </div>
          <div class="upload-area">
            <p><strong>Test PCB Image</strong></p>
            <input type="file" name="test_file" accept="image/png,image/jpeg,image/jpg,image/bmp" required>
          </div>
        </div>
        <p><button class="action" type="submit">Upload & Detect</button></p>
      </form>
      {% if message %}<div class="status">{{ message }}</div>{% endif %}
    </div>

    {% if annotated %}
      <div class="card">
        <div style="display: flex; gap: 18px; align-items: flex-start; justify-content: center;">
          <div style="flex:1; text-align:center;">
            <h2 style="margin-bottom:8px;">ORIGINAL BOARD</h2>
            <img src="{{ original_url }}" class="output-img" alt="Original template" style="max-width:100%; max-height:220px;" />
          </div>
          <div style="flex:1; text-align:center;">
            <h2 style="margin-bottom:8px;">SUBTRACTION MAP</h2>
            <img src="{{ subtraction_url }}" class="subtraction-img" alt="Subtraction map" />
          </div>
          <div style="flex:1; text-align:center;">
            <h2 style="margin-bottom:8px;">AI DETECTION</h2>
            <img src="{{ annotated_url }}" class="output-img" alt="Annotated result" style="max-width:100%; max-height:220px;" />
          </div>
        </div>
        <div class="stats">
          <div class="chip"><strong>Predicted class:</strong> {{ pred_class }}</div>
          <div class="chip"><strong>Defect type:</strong> {{ defect_type }}</div>
          <div class="chip"><strong>Confidence:</strong> {{ confidence }}</div>
          <div class="chip"><strong>Template:</strong> {{ template_name }}</div>
          <div class="chip"><strong>Test image:</strong> {{ test_name }}</div>
        </div>
      </div>
    {% endif %}

  </div>
</body>
</html>
'''


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def append_history(template_name, test_name, pred_class, defect_type, confidence, annotated_name):
    with open(HISTORY_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.datetime.now().isoformat(),
            template_name,
            test_name,
            pred_class,
            defect_type,
            confidence,
            annotated_name
        ])


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    message = None
    annotated = False
    annotated_url = None
    pred_class = None
    confidence = None
    defect_type = 'unknown'
    template_name = None
    test_name = None

    if request.method == 'POST':
        if 'template_file' not in request.files or 'test_file' not in request.files:
            message = 'Both template and test file inputs are required.'
            return render_template_string(HTML_TEMPLATE, message=message)

        template_file = request.files['template_file']
        test_file = request.files['test_file']

        if template_file.filename == '' or test_file.filename == '':
            message = 'Both template and test image files must be selected.'
            return render_template_string(HTML_TEMPLATE, message=message)

        if (template_file and allowed_file(template_file.filename) and
                test_file and allowed_file(test_file.filename)):
            template_name = secure_filename(template_file.filename)
            test_name = secure_filename(test_file.filename)

            template_path = os.path.join(app.config['UPLOAD_FOLDER'], f'template_{template_name}')
            test_path = os.path.join(app.config['UPLOAD_FOLDER'], f'test_{test_name}')

            template_file.save(template_path)
            test_file.save(test_path)

            defect_type = detect_defect_type(test_name)

            model = load_model()
            result = predict_image(test_path, model)
            pred_class = result['class']
            confidence = f"{result['confidence']:.2%}"

            annotated_name = f"annotated_{test_name}"
            annotated_path = os.path.join(app.config['OUTPUT_FOLDER'], annotated_name)
            annotate_image(test_path, annotated_path, model=model)

            subtraction_name = f"subtraction_{test_name}"
            subtraction_path = os.path.join(app.config['OUTPUT_FOLDER'], subtraction_name)
            compute_subtraction(template_path, test_path, subtraction_path)

            annotated = True
            original_url = url_for('uploaded_file', filename=f"template_{template_name}")
            subtraction_url = url_for('web_output_file', filename=subtraction_name)
            annotated_url = url_for('web_output_file', filename=annotated_name)

            # Store last results for PDF
            global last_original_path, last_subtraction_path, last_annotated_path, last_pred_class, last_defect_type, last_confidence, last_template_name, last_test_name
            last_original_path = template_path
            last_subtraction_path = subtraction_path
            last_annotated_path = annotated_path
            last_pred_class = pred_class
            last_defect_type = defect_type
            last_confidence = confidence
            last_template_name = template_name
            last_test_name = test_name

            append_history(template_name, test_name, pred_class, defect_type, confidence, annotated_name)

            message = f'Detection complete: {pred_class} ({defect_type}).'
        else:
            message = 'Invalid file format. Use png, jpg, jpeg, bmp.'

    return render_template_string(
        HTML_TEMPLATE,
        message=message,
        annotated=annotated,
        annotated_url=annotated_url,
        original_url=original_url if 'original_url' in locals() else None,
        subtraction_url=subtraction_url if 'subtraction_url' in locals() else None,
        pred_class=pred_class,
        confidence=confidence,
        defect_type=defect_type,
        template_name=template_name,
        test_name=test_name
    )


@app.route('/history')
def history():
    rows = []
    if os.path.exists(HISTORY_CSV):
        with open(HISTORY_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                rows.append(row)

    history_template = '''
    <!doctype html>
    <html lang="en">
    <head><meta charset="utf-8"/><title>History</title></head>
    <body style="background:#07101d;color:#e9eff6;font-family:sans-serif;padding:20px;">
      <h1>PCB Detection History</h1>
      <a href="/">Back</a> | <a href="/download-report">Download PDF</a>
      <table border="1" cellspacing="0" cellpadding="5" style="margin-top:12px;border-color:#2f3f59;">
        <tr><th>ts</th><th>template</th><th>test</th><th>pred</th><th>defect_type</th><th>conf</th><th>annotated</th></tr>
        {% for r in rows %}
          <tr>
            <td>{{ r.timestamp }}</td>
            <td>{{ r.template_file }}</td>
            <td>{{ r.test_file }}</td>
            <td>{{ r.pred_class }}</td>
            <td>{{ r.defect_type }}</td>
            <td>{{ r.confidence }}</td>
            <td><a href="/web_output/{{ r.annotated_file }}" target="_blank">open</a></td>
          </tr>
        {% endfor %}
      </table>
    </body>
    </html>
    '''
    return render_template_string(history_template, rows=rows)


@app.route('/download-report')
def download_report():
    # Ensure all required results exist
    missing = []
    if not last_original_path or not os.path.exists(last_original_path):
        missing.append('Original Board image')
    if not last_subtraction_path or not os.path.exists(last_subtraction_path):
        missing.append('Subtraction Map image')
    if not last_annotated_path or not os.path.exists(last_annotated_path):
        missing.append('AI Detection image')
    if not last_pred_class or not last_defect_type or not last_confidence or not last_template_name or not last_test_name:
        missing.append('Detection metadata')
    if missing:
        return f"Cannot generate report. Missing: {', '.join(missing)}. Please run a detection first.", 400

    # Mock data for demonstration (replace with real data as needed)
    scan_duration = "1.57s"
    reference_template = last_template_name or "-"
    defect_distribution = {last_defect_type: 1} if last_defect_type else {"Unknown": 1}
    anomalies = [
        {"id": 1, "category": last_defect_type or "-", "severity": "WARNING", "coords": "100, 200", "status": "ACTION REQUIRED"},
    ]

    # Create PDF in memory
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    # Header
    c.setFillColorRGB(0.29, 0.86, 1.0)  # Light blue
    c.setFont("Helvetica-Bold", 22)
    c.drawString(40, y, "VISIONCORE")
    c.setFillColorRGB(0.8, 0.85, 0.9)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(170, y, "AI REPORT")
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica", 10)
    c.drawString(40, y-15, "Industrial Automated Optical Inspection")
    y -= 40

    # Scan duration and reference template
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "SCAN DURATION")
    c.drawString(220, y, "REFERENCE TEMPLATE")
    c.setFont("Helvetica", 12)
    c.drawString(40, y-15, scan_duration)
    c.drawString(220, y-15, reference_template)
    y -= 50

    # Images row
    img_height = 100
    img_width = 120
    x0 = 40
    x1 = x0 + img_width + 30
    x2 = x1 + img_width + 30
    c.setFont("Helvetica-Bold", 10)
    c.drawString(x0, y, "1. ORIGINAL BOARD")
    c.drawString(x1, y, "2. SUBTRACTION MAP")
    c.drawString(x2, y, "3. AI DETECTION (MATCHED)")
    y -= 10
    c.drawImage(ImageReader(last_original_path), x0, y-img_height, width=img_width, height=img_height)
    c.drawImage(ImageReader(last_subtraction_path), x1, y-img_height, width=img_width, height=img_height)
    c.drawImage(ImageReader(last_annotated_path), x2, y-img_height, width=img_width, height=img_height)
    y -= img_height + 30

    # Defect Distribution
    c.setFillColorRGB(0.07, 0.82, 1.0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, "DEFECT DISTRIBUTION")
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica", 11)
    x = 40
    for defect, count in defect_distribution.items():
        c.rect(x, y-18, 60, 16, fill=0)
        c.drawString(x+5, y-15, f"{defect.upper()}: {count}")
        x += 70
    y -= 35

    # Anomalies Table
    c.setFillColorRGB(0.07, 0.82, 1.0)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, f"Analysis Findings: {len(anomalies)} Anomalies Detected")
    y -= 18
    c.setFillColorRGB(0.8, 0.85, 0.9)
    c.rect(40, y-16, 400, 16, fill=1)
    c.setFillColorRGB(0,0,0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(45, y-13, "ID")
    c.drawString(70, y-13, "Category")
    c.drawString(140, y-13, "Severity")
    c.drawString(210, y-13, "Coordinates (X, Y)")
    c.drawString(320, y-13, "Status")
    y -= 16
    c.setFont("Helvetica", 10)
    for anomaly in anomalies:
        c.drawString(45, y-13, str(anomaly["id"]))
        c.drawString(70, y-13, anomaly["category"].capitalize())
        c.setFillColorRGB(1, 0.8, 0.1)
        c.rect(140, y-16, 55, 14, fill=1)
        c.setFillColorRGB(0,0,0)
        c.drawString(143, y-13, anomaly["severity"])
        c.drawString(210, y-13, anomaly["coords"])
        c.setFillColorRGB(1, 0.2, 0.2)
        c.rect(320, y-16, 90, 14, fill=1)
        c.setFillColorRGB(1,1,1)
        c.drawString(323, y-13, anomaly["status"])
        c.setFillColorRGB(0,0,0)
        y -= 16

    c.save()
    buffer.seek(0)
    from flask import send_file
    return send_file(buffer, as_attachment=True, download_name='defect_report.pdf', mimetype='application/pdf')


@app.route('/uploaded/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/web_output/<path:filename>')
def web_output_file(filename):
    return send_from_directory(app.config['OUTPUT_FOLDER'], filename)


@app.route('/analysis/<path:filename>')
def analysis_file(filename):
    return send_from_directory('analysis', filename)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
