"""
Compute confusion matrix across all dataset splits (train+val+test).
Saves image to `evaluation_report/all_confusion_matrix.png` and prints classification report.
"""
import os
import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, classification_report
from torchvision import datasets
from torch.utils.data import DataLoader, ConcatDataset

from load_dataset import val_test_transform, DATASET_ROOT
from inference import load_trained_model, DEVICE

OUTPUT_DIR = 'evaluation_report'
BATCH_SIZE = 32


def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load model
    model = load_trained_model()

    # Build datasets for train/val/test and concat
    splits = ['train', 'val', 'test']
    datasets_list = []
    for s in splits:
        path = os.path.join(DATASET_ROOT, s)
        if os.path.isdir(path):
            ds = datasets.ImageFolder(path, transform=val_test_transform)
            datasets_list.append(ds)
    
    if not datasets_list:
        print('No dataset splits found under', DATASET_ROOT)
        return

    full_dataset = ConcatDataset(datasets_list)
    loader = DataLoader(full_dataset, batch_size=BATCH_SIZE, shuffle=False, num_workers=0)

    all_preds = []
    all_labels = []

    model.eval()
    with torch.no_grad():
        for inputs, labels in loader:
            inputs = inputs.to(DEVICE)
            outputs = model(inputs)
            _, preds = outputs.max(1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    y_true = np.array(all_labels)
    y_pred = np.array(all_preds)

    # Confusion matrix
    cm = confusion_matrix(y_true, y_pred)
    print('Confusion matrix:\n', cm)

    # Classification report
    print('\nClassification report:\n')
    print(classification_report(y_true, y_pred, target_names=['defect','no_defect']))

    # Plot
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['defect','no_defect'], yticklabels=['defect','no_defect'])
    plt.xlabel('Predicted')
    plt.ylabel('True')
    plt.title('Confusion Matrix - All Splits')
    out_path = os.path.join(OUTPUT_DIR, 'all_confusion_matrix.png')
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()
    print(f'✓ Saved combined confusion matrix to {out_path}')

if __name__ == '__main__':
    main()
