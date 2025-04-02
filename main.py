# Pytorch implementation of sheep and wolves recognition

import torch
import torchvision
from torchvision import transforms
import matplotlib.pyplot as plt
from PIL import Image
import requests
from io import BytesIO
import time
import logging

# Sätt upp loggning
logging.basicConfig(
    filename='my_logfile.log',  # Filnamnet för loggen
    level=logging.INFO,        # Loggnivå (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s'  # Loggformat
)



# Ladda en förtränad Faster R-CNN-modell
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()  # Sätt modellen i eval-läge

# Definiera de transformeringar som behövs för att förbereda data
transform = transforms.Compose([
    transforms.ToTensor(),  # Konvertera bilden till en tensor
])

def fetch_and_analyze_image():
    """Hämtar bild från API och analyserar den med Faster R-CNN"""
    try:
        logging.info("Hämtar bild från API...")
        response = requests.get("http://localhost:8000/get_image")  # Byt ut med din API-url
        
        if response.status_code == 200:
            # Läs in bilden
            logging.info("Bild hämtad framgångsrikt.")
            image = Image.open(BytesIO(response.content)).convert("RGB")
            image_tensor = transform(image).unsqueeze(0)  # Konvertera till tensor och lägg till batch-dimension

            # Kör modellen
            with torch.no_grad():
                prediction = model(image_tensor)


            # Extrahera prediktioner
            boxes = prediction[0]['boxes'].numpy()  # Bounding boxes
            labels = prediction[0]['labels'].numpy()  # Objektklasslabel
            scores = prediction[0]['scores'].numpy()  # Förutsägda sannolikheter

            # Visa bilden med bounding boxes
            logging.info("Visar bild med detekterade objekt.")
            plot_image_with_boxes(image, boxes, labels, scores)

        else:
            logging.error("Fel vid hämtning av bild:", response.status_code)

    except Exception as e:
        logging.error("Något gick fel:", e)

def plot_image_with_boxes(image, boxes, labels, scores, threshold=0.5):
    """Visar bild med detekterade objekt"""
    logging.info("Ritar bild med bounding boxes.")
    plt.imshow(image)
    ax = plt.gca()

    for i in range(len(boxes)):
        if scores[i] > threshold:  # Filtrera låga prediktioner
            box = boxes[i]

            # Rita bounding box
            rect = plt.Rectangle(
                (box[0], box[1]), box[2] - box[0], box[3] - box[1],
                linewidth=2, edgecolor='r', facecolor='none'
            )
            ax.add_patch(rect)

            # Lägg till label och score
            ax.text(box[0], box[1], f'{labels[i]}: {scores[i]:.2f}', color='red', fontsize=12)

    plt.axis('off')
    plt.show()

# Loop för att hämta och analysera bilder var 10:e sekund
while True:
    logging.info("Startar bildanalys...")
    fetch_and_analyze_image()
    time.sleep(10)  # Vänta 10 sekunder innan nästa bild hämtas