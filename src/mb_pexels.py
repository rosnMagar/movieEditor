import os
import requests
from dotenv import load_dotenv

load_dotenv()

PEXELS_API_KEY = os.getenv('PEXELS_API_KEY')

class MB_OnlineVideo():

    def __init__(self, query, per_page=5):
        self.query = query
        self.per_page = per_page
        self.url = f"https://api.pexels.com/videos/search?query={query}&per_page={per_page}&orientation=portrait"

    
    """This module does bla bla bla"""    
    def download(self, destination="."):
        headers = {"Authorization": PEXELS_API_KEY}
        response = requests.get(self.url, headers=headers)

        # randomly chose any first 5 images to preserve variety
        # video_index = random.randint(1, 3)

        if response.status_code == 200:
            data = response.json()
            video = data['videos'][0]
            video_data = requests.get(video['video_files'][0]["link"]).content
            video_name = str(self.query).replace(" ", "_")

            with open(f"{destination}/{video_name}.mp4", "wb") as f:
                f.write(video_data)

            return f"{destination}/{video_name}.mp4", video['user']['name'], video['url']
        
        else:
            raise Exception("Couldn't connect to the API")







    




