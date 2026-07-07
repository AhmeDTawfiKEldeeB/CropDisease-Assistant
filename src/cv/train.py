import torch
import torch.nn as nn
import torch.optim as optim
import os
import time

from src.cv.data_loader import get_data_loaders
from src.cv.model import PlantDiseaseResNet


def train_model():
    data_dir = 'dataset'
    num_classes = 38
    batch_size = 32
    num_epochs = 15
    learning_rate = 0.001
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_loader, valid_loader, class_names = get_data_loaders(data_dir, batch_size=batch_size)
    model = PlantDiseaseResNet(num_classes=num_classes)
    model = model.to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=learning_rate, weight_decay=1e-4)

    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='max', factor=0.1, patience=2)
    best_acc = 0.0

    for epoch in range(num_epochs):
        start_time = time.time()
        print(f"\n[{epoch + 1}/{num_epochs}] Epoch Training...")

        model.train()
        running_loss = 0.0
        correct_train = 0
        total_train = 0
        for images, labels in train_loader:
            images, labels = images.to(device), labels.to(device)

            optimizer.zero_grad()

            outputs = model(images)
            loss = criterion(outputs, labels)

            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            _, predicted = torch.max(outputs, 1)
            total_train += labels.size(0)
            correct_train += (predicted == labels).sum().item()

        train_loss = running_loss / len(train_loader.dataset)
        train_acc = correct_train / total_train

        model.eval()
        val_loss = 0.0
        correct_val = 0
        total_val = 0

        with torch.no_grad():
            for images, labels in valid_loader:
                images, labels = images.to(device), labels.to(device)

                outputs = model(images)
                loss = criterion(outputs, labels)

                val_loss += loss.item() * images.size(0)
                _, predicted = torch.max(outputs, 1)
                total_val += labels.size(0)
                correct_val += (predicted == labels).sum().item()

        val_loss = val_loss / len(valid_loader.dataset)
        val_acc = correct_val / total_val
        scheduler.step(val_acc)

        epoch_time = time.time() - start_time

        print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.4f}")
        print(f"Val Loss:   {val_loss:.4f} | Val Acc:   {val_acc:.4f} | Time: {epoch_time:.2f}s")

        if val_acc > best_acc:
            best_acc = val_acc
            if not os.path.exists('models'):
                os.makedirs('models')
            torch.save(model.state_dict(), 'models/best_model.pth')
            print(f" {best_acc:.4f}")

    print(f"\n {best_acc:.4f}")


if __name__ == '__main__':
    train_model()
    