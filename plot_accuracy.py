import json
import matplotlib.pyplot as plt
import os

# Load training metrics
with open('training_metrics.json', 'r') as f:
    metrics = json.load(f)

# Extract data
epochs = list(range(1, len(metrics['train_acc']) + 1))
train_acc = metrics['train_acc']
val_acc = metrics['val_acc']

# Plot
plt.figure(figsize=(10, 6))
plt.plot(epochs, train_acc, label='Training Accuracy', marker='o')
plt.plot(epochs, val_acc, label='Validation Accuracy', marker='o')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.title('Training and Validation Accuracy over Epochs')
plt.legend()
plt.grid(True)
plt.savefig('accuracy_plot.png')
plt.show()