"""Run a full defect inference + visualization pipeline in one command.

Generates:
- Annotated image for single PCB input (with class, confidence)
- accuracy_plot.png (train/val accuracy from training_metrics.json)
- loss_plot.png (train/val loss from training_metrics.json)
- analysis/cooccurrence_counts.png
- analysis/cooccurrence_normalized.png
- analysis/per_class_counts.png

Usage:
    python run_full_output.py path/to/input_pcb.jpg

"""

import os
import sys
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

from predict_and_annotate import annotate_image, predict_image, load_model


def run_plots():
    subprocess.run([sys.executable, 'plot_accuracy.py'], check=True)
    subprocess.run([sys.executable, 'plot_loss.py'], check=True)


def run_confusion():
    subprocess.run([sys.executable, 'compute_confusion_matrices.py'], check=True)


def main():
    if len(sys.argv) < 2:
        print('Usage: python run_full_output.py <input_image_path> [output_dir]')
        sys.exit(1)

    input_image = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else 'output'
    os.makedirs(output_dir, exist_ok=True)

    model = load_model()
    result = predict_image(input_image, model)
    base_name = os.path.splitext(os.path.basename(input_image))[0]
    annotated_path = os.path.join(output_dir, f'annotated_{base_name}.jpg')

    annotate_image(input_image, annotated_path, model=model)

    print('\nSingle-image prediction result:')
    print(f" - class: {result['class']}")
    print(f" - confidence: {result['confidence']:.2%}")
    print(f" - probs: defect={result['probs'][0]:.4f}, no_defect={result['probs'][1]:.4f}")

    print('\nRunning plotting and analysis tasks (parallel)...')
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(run_plots): 'accuracy+loss',
            executor.submit(run_confusion): 'confusion',
        }

        for future in as_completed(futures):
            name = futures[future]
            try:
                future.result()
                print(f" ✓ {name} generation done")
            except Exception as exc:
                print(f" ✗ {name} failed: {exc}")

    print('\nOutput files:')
    print(f" - Annotated image: {annotated_path}")
    print(' - Accuracy plot: accuracy_plot.png')
    print(' - Loss plot: loss_plot.png')
    print(' - Confusion heatmaps: analysis/cooccurrence_counts.png, analysis/cooccurrence_normalized.png, analysis/per_class_counts.png')

    print('\nDone.')


if __name__ == '__main__':
    main()
