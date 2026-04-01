"""
STEP 4: Load Dataset

Provides utilities for creating PyTorch DataLoaders based on the
`dataset/train|val|test/defect|no_defect` structure created previously.
Images are assumed to already be resized to 128x128; transforms simply
normalize and convert to tensors.
"""

import os
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

# configuration
DATASET_ROOT = './dataset'
IMAGE_SIZE = 128
BATCH_SIZE = 16
NUM_WORKERS = 0

# basic transforms (resize already done)
train_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

val_test_transform = transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])


def make_dataloader(root_dir=DATASET_ROOT, batch_size=BATCH_SIZE, num_workers=NUM_WORKERS):
    """Create train, validation and test DataLoaders.

    Returns:
        dict of {"train": loader, "val": loader, "test": loader} and
        dataset sizes.
    """

    loaders = {}
    sizes = {}

    for split in ['train', 'val', 'test']:
        split_dir = os.path.join(root_dir, split)
        if not os.path.isdir(split_dir):
            raise FileNotFoundError(f"Split directory not found: {split_dir}")

        transform = train_transform if split == 'train' else val_test_transform
        dataset = datasets.ImageFolder(split_dir, transform=transform)
        loader = DataLoader(dataset, batch_size=batch_size,
                            shuffle=(split == 'train'),
                            num_workers=num_workers)

        loaders[split] = loader
        sizes[split] = len(dataset)

    return loaders, sizes


if __name__ == '__main__':
    # quick test to verify data loading
    loaders, sizes = make_dataloader()
    print("Dataset sizes:", sizes)
    sample_batch = next(iter(loaders['train']))
    images, labels = sample_batch
    print("Batch image shape:", images.shape)
    print("Batch labels:", labels[:10])
