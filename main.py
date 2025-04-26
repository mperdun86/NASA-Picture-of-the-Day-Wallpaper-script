import requests
import random
import os
import ctypes
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, date, timedelta
load_dotenv()

#-------[CONSTANTS]-----#
API_KEY = os.getenv('API_KEY')
DOWNLOAD_DIR = Path(os.getenv('SAVE_FOLDER'))
DOWNLOAD_DIR.mkdir(parents=True, exist_ok=True)

#--------[FUNCTIONS]--------#
def get_random_apod_image():
    # June 16, 1995 is the furthest back you can go
    start_date = date(1995, 6, 16)
    end_date = datetime.today().date()
    random_days = random.randint(0, (end_date - start_date).days)
    random_date = start_date + timedelta(days=random_days)

    url = f"https://api.nasa.gov/planetary/apod?api_key={API_KEY}&date={random_date}"

    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        if data.get("media_type") == "image":
            print(f"Title: {data['title']}")
            print(f"Date: {data['date']}")
            print(f"URL: {data['url']}")
            return data['url'], data['title']
        else:
            print(f"The media on {random_date} is not an image. Trying again...")
            return get_random_apod_image()
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return None, None

def download_image(image_url, title):
    response = requests.get(image_url)
    time_now = datetime.now()
    if response.status_code == 200:
        file_name = f"{title.replace(' ', '_')}.jpg"
        file_path = DOWNLOAD_DIR / file_name
        with open(file_path, 'wb') as f:
            f.write(response.content)
        print(f"Image downloaded to {file_path}")

        with open("response_log.txt", "a") as log:
            log.write(f"[{time_now.strftime('%Y-%m-%d %H:%M:%S')}] : {file_name} Successfully downloaded.\n")

        return file_path
    else:
        print(f"Failed to download image: {response.status_code}")
        with open("response_log.txt", "a") as log:
            log.write(f"[{time_now.strftime('%Y-%m-%d %H:%M:%S')}] : Something went wrong! : {response.status_code}.\n")
        return None


def set_wallpaper(image_path):
    SPI_SETDESKWALLPAPER = 20
    result = ctypes.windll.user32.SystemParametersInfoW(SPI_SETDESKWALLPAPER, 0, str(image_path), 3)
    if result:
        print(f"Wallpaper set to {image_path}")
    else:
        print("Failed to set wallpaper.")

#--------[MAIN LOOP]------#

if __name__ == "__main__":
    image_url, title = get_random_apod_image()
    if image_url:
        image_path = download_image(image_url, title)
        if image_path:
            set_wallpaper(image_path)
