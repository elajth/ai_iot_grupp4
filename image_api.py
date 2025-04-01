from fastapi import FastAPI, BackgroundTasks
import asyncio
import random
import time
from pathlib import Path
from fastapi.responses import FileResponse

# Skapa FastAPI-applikation
app = FastAPI()

# Mapp där bilderna finns
image_folder = Path("./random_img")

# Lista över bilder
images = ["wolf.png", "nothing.png"]

# Funktion för att skicka bild var 10:e sekund
async def send_image():
    while True:
        # Välj en bild baserat på sannolikhet
        image_choice = random.choices(images, weights=[0.1, 0.9], k=1)[0]
        image_path = image_folder / image_choice
        
        # Här kan du implementera logiken för att skicka bilden till en klient eller spara den
        print(f"Skickar bild: {image_path}")
        
        # Vänta i 10 sekunder innan nästa bild skickas
        await asyncio.sleep(10)

# Skapa en bakgrundsprocess för att starta bildskickning när appen startar
@app.get("/start_sending_images")
async def start_sending_images(background_tasks: BackgroundTasks):
    background_tasks.add_task(send_image)
    return {"message": "Bilder skickas nu i bakgrunden var 10:e sekund."}

# Endpoint för att hämta aktuell bild
@app.get("/get_image")
async def get_image():
    image_choice = random.choices(images, weights=[0.1, 0.9], k=1)[0]
    image_path = image_folder / image_choice
    return FileResponse(image_path)

# För att testa applikationen, kör FastAPI-servern
# uvicorn app:app --reload
