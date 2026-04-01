import json
import matplotlib.pyplot as plt
import os

# Load training metrics
with open('training_metrics.json', 'r') as f:
    metrics = json.load(f)

# Extract data
epochs = list(range(1, len(metrics['train_loss']) + 1))
train_loss = metrics['train_loss']
val_loss = metrics['val_loss']

# Plot
plt.figure(figsize=(10, 6))
plt.plot(epochs, train_loss, label='Training Loss', marker='o')
plt.plot(epochs, val_loss, label='Validation Loss', marker='o')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.title('Training and Validation Loss over Epochs')
plt.legend()
plt.grid(True)
plt.savefig('loss_plot.png')
plt.show()