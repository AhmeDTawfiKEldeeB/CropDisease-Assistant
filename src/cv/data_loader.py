"""Data loaders for the plant-disease image dataset."""

from pathlib import Path
from typing import Tuple

import torch
from torch.utils.data import DataLoader
from torchvision import datasets, transforms

from src.config import settings


def get_transforms(
    image_size: int = settings.cv.image_size,
) -> Tuple[transforms.Compose, transforms.Compose]:
    """Return train and validation transforms."""
    train_transform = transforms.Compose(
        [
            transforms.RandomResizedCrop(image_size),
            transforms.RandomHorizontalFlip(),
            transforms.RandomRotation(20),
            transforms.ColorJitter(brightness=0.2, contrast=0.2),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=settings.cv.normalize_mean,
                std=settings.cv.normalize_std,
            ),
        ]
    )

    valid_transform = transforms.Compose(
        [
            transforms.Resize(image_size + 32),
            transforms.CenterCrop(image_size),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=settings.cv.normalize_mean,
                std=settings.cv.normalize_std,
            ),
        ]
    )

    return train_transform, valid_transform


def get_data_loaders(
    data_dir: str,
    batch_size: int = 32,
    image_size: int = settings.cv.image_size,
    num_workers: int = 4,
) -> Tuple[DataLoader, DataLoader, list]:
    """
    Build train/validation DataLoaders from ImageFolder splits.

    Expects ``data_dir`` to contain ``train/`` and ``valid/`` subfolders, each
    with one folder per class.

    Args:
        data_dir: Root directory containing ``train`` and ``valid`` folders.
        batch_size: Number of samples per batch.
        image_size: Size to resize/crop images to.
        num_workers: Number of worker processes for data loading.

    Returns:
        train_loader, valid_loader, class_names
    """
    root = Path(data_dir)
    train_dir = root / "train"
    valid_dir = root / "valid"

    if not train_dir.is_dir():
        raise FileNotFoundError(f"Training directory not found: {train_dir}")
    if not valid_dir.is_dir():
        raise FileNotFoundError(f"Validation directory not found: {valid_dir}")

    train_transform, valid_transform = get_transforms(image_size)

    train_dataset = datasets.ImageFolder(root=str(train_dir), transform=train_transform)
    valid_dataset = datasets.ImageFolder(root=str(valid_dir), transform=valid_transform)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=True,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )
    valid_loader = DataLoader(
        valid_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=torch.cuda.is_available(),
    )

    return train_loader, valid_loader, train_dataset.classes
