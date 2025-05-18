import os
import requests
from dotenv import load_dotenv
import random

load_dotenv()

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

class MB_OnlineImage():

    def __init__(self, query, per_page=5):
        self.query = query
        self.per_page = per_page
        self.url = f"https://api.pexels.com/v1/search?query={query}&per_page={per_page}"

    
    """This module does bla bla bla"""    
    def download(self, destination="."):
        headers = {"Authorization": PEXELS_API_KEY}
        response = requests.get(self.url, headers=headers)

        # randomly chose any first 5 images to preserve variety
        image_index = random.randint(1, 3)

        if response.status_code == 200:
            data = response.json()
            photo = data['photos'][image_index]
            image_data = requests.get(photo['src']['medium']).content
            image_name = str(self.query).replace(" ", "_")

            with open(f"{destination}/{image_name}.jpg", "wb") as f:
                f.write(image_data)

            return f"{destination}/{image_name}.jpg", photo['photographer'], photo['src']['medium']
        
        else:
            raise Exception("Couldn't connect to the API")







    




