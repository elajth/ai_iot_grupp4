# Pytorch implementation of sheep and wolves recognition

import torch
import torchvision
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import Image

# Ladda en förtränad Faster R-CNN-modell
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()  # Sätt modellen i eval-läge

# Definiera de transformeringar som behövs för att förbereda data
transform = transforms.Compose([
    transforms.ToTensor(),  # Konvertera bilden till en tensor
])

# Ladda en bild
image_path = './wolves/Eurasian_wolfJPG.jpg'  # Sätt din bildväg här
image = Image.open(image_path).convert("RGB")

# Applicera transformeringarna på bilden
image_tensor = transform(image).unsqueeze(0)  # Lägg till en extra dimension för batchen

with torch.no_grad():  # Ingen behov av att beräkna gradienter
    prediction = model(image_tensor)

# Extract the predictions
boxes = prediction[0]['boxes'].numpy()  # Bounding boxes
labels = prediction[0]['labels'].numpy()  # Objektklasslabel
scores = prediction[0]['scores'].numpy()  # Förutsägda sannolikheter

def plot_image_with_boxes(image, boxes, labels, scores, threshold=0.5):
    plt.imshow(image)
    ax = plt.gca()

    # Loop through the boxes and plot them
    for i in range(len(boxes)):
        if scores[i] > threshold:  # Skippa låga förutsägelser
            box = boxes[i]
            label = labels[i]
            score = scores[i]

            # Rita en bounding box
            rect = plt.Rectangle(
                (box[0], box[1]), box[2] - box[0], box[3] - box[1],
                linewidth=2, edgecolor='r', facecolor='none'
            )
            ax.add_patch(rect)

            # Lägg till label och score
            ax.text(box[0], box[1], f'{label}: {score:.2f}', color='red', fontsize=12)

    plt.axis('off')
    plt.show()

# Visa bild med bounding boxes
plot_image_with_boxes(image, boxes, labels, scores)

if __name__ == "__main__":
    # Kör koden här om den körs som ett skript
    plot_image_with_boxes(image, boxes, labels, scores)