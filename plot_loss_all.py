import json
import torch
import matplotlib.pyplot as plt

from load_dataset import make_dataloader
from inference import load_trained_model, DEVICE

# Load training metrics
with open('training_metrics.json', 'r') as f:
    metrics = json.load(f)

# Prepare data loaders
loaders, sizes = make_dataloader()

# Load model and criterion
model = load_trained_model()
model.eval()
criterion = torch.nn.CrossEntropyLoss()

# Compute test loss
test_loss = 0.0
num_samples = 0
with torch.no_grad():
    for inputs, labels in loaders['test']:
        inputs = inputs.to(DEVICE)
        labels = labels.to(DEVICE)
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        batch_size = inputs.size(0)
        test_loss += loss.item() * batch_size
        num_samples += batch_size

if num_samples > 0:
    test_loss /= num_samples

# Prepare loss data (use last epoch losses for train/val)
train_loss = metrics['train_loss'][-1]
val_loss = metrics['val_loss'][-1]

splits = ['Train', 'Validation', 'Test']
losses = [train_loss, val_loss, test_loss]

# Plot
plt.figure(figsize=(8, 6))
bars = plt.bar(splits, losses, color=['blue', 'orange', 'green'])
plt.ylabel('Loss')
plt.title('Loss on All Dataset Splits')
plt.grid(axis='y', linestyle='--', alpha=0.7)

for bar, loss in zip(bars, losses):
    plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01, f'{loss:.4f}', 
             ha='center', va='bottom', fontweight='bold')

plt.savefig('loss_all_splits.png')
plt.show()
