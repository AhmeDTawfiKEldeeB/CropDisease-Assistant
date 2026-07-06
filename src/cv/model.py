import torch
import torch.nn as nn
from torchvision import models


class PlantDiseaseResNet(nn.Module):
    def __init__(self, num_classes=38):
        super(PlantDiseaseResNet, self).__init__()

        self.base_model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)

        num_ftrs = self.base_model.fc.in_features

        self.base_model.fc = nn.Sequential(
            nn.Dropout(p=0.5),
            nn.Linear(num_ftrs, 512),
            nn.BatchNorm1d(512),
            nn.ReLU(),
            nn.Dropout(p=0.3),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.base_model(x)


if __name__ == "__main__":
    model = PlantDiseaseResNet(num_classes=38)

    dummy_image = torch.randn(2, 3, 224, 224)

    output = model(dummy_image)
