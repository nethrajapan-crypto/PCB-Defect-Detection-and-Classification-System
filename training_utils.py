"""
STEP 6: Define Loss & Optimizer

Provides helper functions for creating loss criterion and optimizer for
training the defect detection model.
"""

import torch
import torch.nn as nn
import torch.optim as optim


def get_loss_and_optimizer(model, learning_rate=1e-4, weight_decay=1e-5):
    """Return a loss function and optimizer for model training.

    Args:
        model (torch.nn.Module): network to optimize
        learning_rate (float): base LR
        weight_decay (float): L2 regularization
    Returns:
        criterion, optimizer
    """
    # Binary classification: use cross-entropy
    criterion = nn.CrossEntropyLoss()

    # AdamW optimizer is generally good for transfer learning
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate,
                             weight_decay=weight_decay)
    return criterion, optimizer


def save_checkpoint(model, optimizer, epoch, path):
    """Save model and optimizer state to a checkpoint file."""
    state = {
        'epoch': epoch,
        'model_state': model.state_dict(),
        'optimizer_state': optimizer.state_dict()
    }
    torch.save(state, path)


def load_checkpoint(model, optimizer, path, device=None):
    """Load checkpoint into model and optimizer.

    If `device` is provided it will be used when loading the state dicts.
    Returns the epoch number stored in the checkpoint.
    """
    if device is None:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    checkpoint = torch.load(path, map_location=device)
    model.load_state_dict(checkpoint['model_state'])
    optimizer.load_state_dict(checkpoint['optimizer_state'])
    return checkpoint.get('epoch', None)


if __name__ == '__main__':
    # quick self-test
    from model import create_model

    m = create_model()
    crit, opt = get_loss_and_optimizer(m)
    print("criterion", crit)
    print("optimizer", opt)

