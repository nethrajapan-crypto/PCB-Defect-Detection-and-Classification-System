"""
Final Reporting & Visualization

Generates a comprehensive HTML report with all metrics, visualizations,
and model information.
"""

import os
import json
from pathlib import Path


def create_html_report(eval_dir='evaluation_report', output_file='report.html'):
    """Create an HTML report combining all evaluation results."""
    
    # Load metrics
    report_json = os.path.join(eval_dir, 'evaluation_report.json')
    if not os.path.exists(report_json):
        print(f"Error: {report_json} not found. Run evaluate.py first.")
        return
    
    with open(report_json) as f:
        report = json.load(f)
    
    # Build HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>PCB Defect Detection - Evaluation Report</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                border-radius: 10px;
                margin-bottom: 30px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }}
            .header h1 {{
                margin: 0;
                font-size: 2.5em;
            }}
            .section {{
                background: white;
                padding: 30px;
                margin-bottom: 20px;
                border-radius: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                color: #667eea;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
                margin-top: 0;
            }}
            .metrics-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .metric-card {{
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                border-left: 4px solid #667eea;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                color: #667eea;
            }}
            .metric-label {{
                color: #666;
                font-size: 0.9em;
                margin-top: 5px;
            }}
            .image-container {{
                text-align: center;
                margin: 30px 0;
            }}
            .image-container img {{
                max-width: 100%;
                height: auto;
                border-radius: 8px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .image-caption {{
                color: #666;
                margin-top: 10px;
                font-style: italic;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
            }}
            th {{
                background: #f8f9fa;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #333;
                border-bottom: 2px solid #667eea;
            }}
            td {{
                padding: 12px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            .footer {{
                text-align: center;
                color: #999;
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #eee;
            }}
            .positive {{ color: #28a745; font-weight: bold; }}
            .negative {{ color: #dc3545; font-weight: bold; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔬 PCB Defect Detection Report</h1>
            <p>Comprehensive Evaluation of EfficientNet-B0 Classification Model</p>
        </div>
        
        <div class="section">
            <h2>📊 Model Performance Overview</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value">{report['test_metrics']['accuracy']:.2%}</div>
                    <div class="metric-label">Test Accuracy</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['test_metrics']['roc_auc']:.4f}</div>
                    <div class="metric-label">ROC-AUC Score</div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">{report['dataset']['total_samples']}</div>
                    <div class="metric-label">Test Samples</div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Training Progress</h2>
            <div class="image-container">
                <img src="training_curves.png" alt="Training Curves">
                <div class="image-caption">Loss and Accuracy over Training Epochs</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎯 Confusion Matrix</h2>
            <div class="image-container">
                <img src="confusion_matrix.png" alt="Confusion Matrix">
                <div class="image-caption">Predicted vs. True Labels on Test Set</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📉 ROC Curve</h2>
            <div class="image-container">
                <img src="roc_curve.png" alt="ROC Curve">
                <div class="image-caption">Receiver Operating Characteristic Curve</div>
            </div>
        </div>
        
        <div class="section">
            <h2>📋 Classification Metrics by Class</h2>
            <table>
                <tr>
                    <th>Class</th>
                    <th>Precision</th>
                    <th>Recall</th>
                    <th>F1-Score</th>
                    <th>Support</th>
                </tr>
    """
    
    # Add per-class metrics
    for class_name in ['defect', 'no_defect']:
        metrics = report['class_metrics'][class_name]
        html += f"""
                <tr>
                    <td><strong>{class_name.upper()}</strong></td>
                    <td>{metrics['precision']:.4f}</td>
                    <td>{metrics['recall']:.4f}</td>
                    <td>{metrics['f1-score']:.4f}</td>
                    <td>{int(metrics['support'])}</td>
                </tr>
        """
    
    # Add error analysis
    fp = report['error_analysis']['false_positives']
    fn = report['error_analysis']['false_negatives']
    
    html += f"""
            </table>
        </div>
        
        <div class="section">
            <h2>⚠️ Error Analysis</h2>
            <div class="metrics-grid">
                <div class="metric-card">
                    <div class="metric-value negative">{fp['count']}</div>
                    <div class="metric-label">False Positives</div>
                    <div style="font-size: 0.85em; color: #666; margin-top: 10px;">
                        Avg Conf: {fp['avg_confidence']:.2%}
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value negative">{fn['count']}</div>
                    <div class="metric-label">False Negatives</div>
                    <div style="font-size: 0.85em; color: #666; margin-top: 10px;">
                        Avg Conf: {fn['avg_confidence']:.2%}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔧 Model Configuration</h2>
            <table>
                <tr>
                    <th>Parameter</th>
                    <th>Value</th>
                </tr>
                <tr>
                    <td>Architecture</td>
                    <td>{report['model']['architecture']}</td>
                </tr>
                <tr>
                    <td>Pretrained</td>
                    <td>{'Yes' if report['model']['pretrained'] else 'No'}</td>
                </tr>
                <tr>
                    <td>Input Size</td>
                    <td>128 × 128</td>
                </tr>
                <tr>
                    <td>Number of Classes</td>
                    <td>2 (Defect / No-Defect)</td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>📊 Dataset Summary</h2>
            <table>
                <tr>
                    <th>Class</th>
                    <th>Count</th>
                    <th>Percentage</th>
                </tr>
                <tr>
                    <td>Defect</td>
                    <td>{report['dataset']['defect_samples']}</td>
                    <td>{report['dataset']['defect_samples'] / report['dataset']['total_samples']:.1%}</td>
                </tr>
                <tr>
                    <td>No-Defect</td>
                    <td>{report['dataset']['no_defect_samples']}</td>
                    <td>{report['dataset']['no_defect_samples'] / report['dataset']['total_samples']:.1%}</td>
                </tr>
                <tr>
                    <td><strong>Total</strong></td>
                    <td><strong>{report['dataset']['total_samples']}</strong></td>
                    <td><strong>100.0%</strong></td>
                </tr>
            </table>
        </div>
        
        <div class="section">
            <h2>📋 How to Use This Model</h2>
            <pre style="background: #f8f9fa; padding: 15px; border-radius: 5px; overflow-x: auto;">
from predict_and_annotate import load_model, predict_image

# Load the trained model
model = load_model()

# Make prediction on an image
result = predict_image('test_image.jpg', model)
print(f"Prediction: {{result['class']}} (confidence: {{result['confidence']:.2%}})")

# Annotate image with prediction
from predict_and_annotate import annotate_image
annotate_image('test_image.jpg', 'output.jpg', model)
            </pre>
        </div>
        
        <div class="footer">
            <p>Generated: {Path(eval_dir).absolute()}</p>
            <p>Model: EfficientNet-B0 | Framework: PyTorch</p>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(output_file, 'w') as f:
        f.write(html)
    
    print(f"✓ HTML report saved: {output_file}")


if __name__ == '__main__':
    create_html_report()
