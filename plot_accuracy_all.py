import json
import matplotlib.pyplot as plt
import os

# Load training metrics
with open('training_metrics.json', 'r') as f:
    metrics = json.load(f)

# Load evaluation report for test accuracy
with open('evaluation_report/evaluation_report.json', 'r') as f:
    eval_report = json.load(f)

# Get final accuracies
train_acc = metrics['train_acc'][-1]  # Last epoch train accuracy
val_acc = metrics['val_acc'][-1]      # Last epoch val accuracy
test_acc = eval_report['test_metrics']['accuracy']  # Test accuracy

# Data for bar plot
splits = ['Train', 'Validation', 'Test']
accuracies = [train_acc, val_acc, test_acc]

# Plot
plt.figure(figsize=(8, 6))
bars = plt.bar(splits, accuracies, color=['blue', 'orange', 'green'])
plt.ylabel('Accuracy')
plt.title('Accuracy on All Dataset Splits')
plt.ylim(0, 1.1)  # Set y-axis from 0 to 1.1 for better visualization
plt.grid(axis='y', linestyle='--', alpha=0.7)

# Add value labels on bars
for bar, acc in zip(bars, accuracies):
    plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, f'{acc:.4f}', 
             ha='center', va='bottom', fontweight='bold')

plt.savefig('accuracy_all_splits.png')
plt.show()