import os
import re
import time
import shutil

from PIL import Image
from google import genai
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

WATCH_FOLDER = "captcha_dataset"
PROCESSED_FOLDER = "captcha_processed"
FAILED_FOLDER = "captcha_failed"

client = genai.Client(
    api_key="odgovarajuci api gemini flash 3.6 kljuc"
)

prompt = """
Read the captcha image.

The image contains two integers and a plus sign.

Calculate the sum.

Return only the resulting number.
"""

def process_image(filepath):
    try:
        img = Image.open(filepath)

        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=[
                prompt,
                img
            ]
        )

        result = response.text.strip()

        if re.fullmatch(r"\d+", result):
        #ako se vrati samo broj, sliku captche premestamo u captcha_processed, rezultat se vraca
            shutil.move(
                filepath,
                os.path.join(
                    PROCESSED_FOLDER,
                    os.path.basename(filepath)
                )
            )
            print(result) #cisto za testiranje
            return int(result)

        else: #u suprotnom, pomera se u captcha_failed
            shutil.move(
                filepath,
                os.path.join(
                    FAILED_FOLDER,
                    os.path.basename(filepath)
                )
            )

    except Exception as e:
        print(f"ERROR: {e}")
        try:
            shutil.move(
                filepath,
                os.path.join(
                    FAILED_FOLDER,
                    os.path.basename(filepath)
                )
            )
        except Exception as move_error:
            print(f"MOVE ERROR: {move_error}")

class ImageHandler(FileSystemEventHandler):

    def on_created(self, event):

        if event.is_directory:
            return

        # sacekaj da se fajl dokopira
        time.sleep(2)

        ext = os.path.splitext(
            event.src_path
        )[1].lower()

        if ext in [".png", ".jpg", ".jpeg"]:
            process_image(event.src_path)

os.makedirs(
    WATCH_FOLDER,
    exist_ok=True
)

os.makedirs(
    PROCESSED_FOLDER,
    exist_ok=True
)

os.makedirs(
    FAILED_FOLDER,
    exist_ok=True
)

for filename in os.listdir(WATCH_FOLDER):

    if filename.lower().endswith(
        (".png", ".jpg", ".jpeg")
    ):

        process_image(
            os.path.join(
                WATCH_FOLDER,
                filename
            )
        )
observer = Observer()

observer.schedule(
    ImageHandler(),
    WATCH_FOLDER,
)

observer.start()

try:
    while True:
        time.sleep(1)

except KeyboardInterrupt:
    observer.stop()

observer.join()