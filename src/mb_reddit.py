from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from PIL import Image
import time

TMP_DIR = "./tmp"
class MBReddit():
    def __init__(self, url):
        self.url = url

    def get_post_screenshot(self):

        mobile_emulation = {
            "deviceName": "iPhone 12 Pro"
        }

        chrome_options = Options()
        chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

        driver = webdriver.Chrome(options=chrome_options)
        driver.get(self.url)

        shadow_parent = driver.find_element(By.XPATH, "/html/body/shreddit-app/div[3]/div[1]/div/main/shreddit-post")
        shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_parent)

        credit_bar = driver.find_element(By.XPATH, "/html/body/shreddit-app/div[3]/div[1]/div/main/shreddit-post/div[1]")
        title_bar = driver.find_element(By.XPATH, "/html/body/shreddit-app/div[3]/div[1]/div/main/shreddit-post/h1")
        interaction_bar = shadow_root.find_element(By.CSS_SELECTOR, "[data-testid='action-row']")
        

        credit_bar.screenshot(f"{TMP_DIR}/credit_bar.png")
        title_bar.screenshot(f"{TMP_DIR}/title_bar.png")
        interaction_bar.screenshot(f"{TMP_DIR}/interaction_bar.png")

        driver.quit()

        credit_bar_image = Image.open(f"{TMP_DIR}/credit_bar.png")
        title_bar_image = Image.open(f"{TMP_DIR}/title_bar.png")
        interaction_bar_image = Image.open(f"{TMP_DIR}/interaction_bar.png")

        w1, h1 = credit_bar_image.size
        w2, h2 = title_bar_image.size
        w3, h3 = interaction_bar_image.size

        new_width = max(w1, w2, w3)
        new_height = h1 + h2 + h3

        stitched_image = Image.new("RGB", (new_width, new_height))

        stitched_image.paste(credit_bar_image, (0, 0))
        stitched_image.paste(title_bar_image, (0, h1))
        stitched_image.paste(interaction_bar_image, (0, h1 + h2))

        stitched_image.save(f'{TMP_DIR}/reddit_topic.png')


# ss = MBReddit('https://www.reddit.com/r/Millennials/comments/1kryeks/did_we_get_ripped_off_with_homework/')
# ss.get_post_screenshot()

