import torch
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import os
from src.model import PlantDiseaseResNet


def predict_disease(image_path, model_path='models/best_model.pth', dataset_dir='dataset/train'):

    if not os.path.exists(image_path):
        return f" {image_path}", 0
    if not os.path.exists(model_path):
        return f"❌", 0

    try:
        class_names = sorted(os.listdir(dataset_dir))
    except FileNotFoundError:
        return "❌ dataset/train", 0
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    transform = transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0)
    image_tensor = image_tensor.to(device)

    model = PlantDiseaseResNet(num_classes=len(class_names))
    model.load_state_dict(torch.load(model_path, map_location=device))
    model.to(device)

    model.eval()

    with torch.no_grad():
        output = model(image_tensor)
        probabilities = F.softmax(output[0], dim=0)
        confidence, predicted_idx = torch.max(probabilities, 0)
    predicted_class = class_names[predicted_idx.item()]
    confidence_percentage = confidence.item() * 100

    return predicted_class, confidence_percentage


if __name__ == '__main__':
    test_image_path = 'test_leaf.png'

    predicted_disease, confidence = predict_disease(test_image_path)

    if confidence > 0:
        print("\n" + "=" * 50)
        print(f" {predicted_disease}")
        print(f" {confidence:.2f}%")
        print("=" * 50 + "\n")
    else:
        print(predicted_disease)