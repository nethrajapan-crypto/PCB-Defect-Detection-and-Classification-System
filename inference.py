"""
STEP 8: Inference & Evaluation

Load the saved checkpoint and run inference on the test set or single images.
Provides utilities to compute confusion matrix and display predictions.
"""

import os
import torch
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
from load_dataset import make_dataloader
from model import create_model

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CHECKPOINT_PATH = './best_model.pth'


def load_trained_model(path=CHECKPOINT_PATH, model_name='efficientnet_b0'):
    model = create_model(model_name=model_name, pretrained=False)
    model.load_state_dict(torch.load(path, map_location=DEVICE))
    model.to(DEVICE)
    model.eval()
    return model


def run_test_evaluation():
    loaders, sizes = make_dataloader()
    model = load_trained_model()

    all_preds = []
    all_labels = []

    with torch.no_grad():
        for inputs, labels in loaders['test']:
            inputs = inputs.to(DEVICE)
            outputs = model(inputs)
            _, preds = outputs.max(1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.numpy())

    cm = confusion_matrix(all_labels, all_preds)
    report = classification_report(all_labels, all_preds, target_names=['defect','no_defect'])
    print("Confusion Matrix:\n", cm)
    print("\nClassification Report:\n", report)


def predict_image(image_tensor, model=None):
    if model is None:
        model = load_trained_model()

    image_tensor = image_tensor.to(DEVICE).unsqueeze(0)
    with torch.no_grad():
        out = model(image_tensor)
        _, pred = out.max(1)
    return pred.item()


def export_torchscript(model_path=CHECKPOINT_PATH, output_path='./model_script.pt', model_name='efficientnet_b0'):
    """Load the trained model and save as a TorchScript file."""
    model = load_trained_model(path=model_path, model_name=model_name)
    # create dummy input for tracing
    dummy = torch.randn(1,3,128,128).to(DEVICE)
    scripted = torch.jit.trace(model, dummy)
    scripted.save(output_path)
    print(f"TorchScript model saved to {output_path}")


def main():
    print("Running evaluation on test set...")
    run_test_evaluation()

if __name__ == '__main__':
    main()
