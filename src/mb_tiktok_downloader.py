import os
import time
import requests
# Assuming mb_util is a custom module you have with a snake_case function
import mb_util

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Re-importing webdriver_manager and Service for robust driver management
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

def download_tiktok_videos_by_keyword(keyword, num_videos=5, output_dir="./tmp"):
    """
    Downloads TikTok videos based on a given keyword.

    Args:
        keyword (str): The keyword to search for on TikTok.
        num_videos (int): The maximum number of videos to attempt to download.
        output_dir (str): The directory where videos will be saved.
    """

    # --- Setup Chrome Options ---
    chrome_options = Options()

    # --- IMPORTANT: Chrome Profile Configuration (TEMPORARILY COMMENTED OUT FOR TESTING) ---
    # Keep these commented out until the basic browser launch is stable.
    # user_data_dir = "C:\\Users\\Dell\\AppData\\Local\\Google\\Chrome\\User Data"
    # profile_name = "Profile 13"
    # chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    # chrome_options.add_argument(f"--profile-directory={profile_name}")
    # --- End Chrome Profile Configuration ---

    # Mobile emulation settings (currently commented out)
    # mobile_emulation = {
    #     "deviceName": "iPhone 12 Pro"
    # }
    # chrome_options.add_experimental_option("mobileEmulation", mobile_emulation)

    # Common arguments to prevent Chrome crashes and improve stability
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--remote-debugging-port=9222") # Add a remote debugging port
    chrome_options.add_argument("--disable-browser-side-navigation") # Helps with some navigation issues
    chrome_options.add_argument("--disable-gpu") # Recommended, especially for headless, but good practice
    chrome_options.add_argument("--start-maximized") # Start maximized, can help with element visibility

    # Enable headless mode for stability during testing
    chrome_options.add_argument("--headless")


    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--window-size=1920,1080") # Useful even in headless for consistent layout
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])


    # --- Initialize WebDriver ---
    # Using ChromeDriverManager to automatically download and manage the Chrome driver
    print("Initializing Chrome WebDriver...")
    try:
        service = Service(ChromeDriverManager().install()) # Use Service with ChromeDriverManager
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("WebDriver initialized successfully.")
    except Exception as e:
        print(f"Error initializing WebDriver: {e}")
        print("Please ensure you have Google Chrome installed and that your internet connection is stable.")
        print("`webdriver_manager` is being used. If issues persist, refer to the troubleshooting steps below.")
        return

    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created output directory: {output_dir}")

    # Construct the TikTok search URL
    search_url = f"https://www.tiktok.com/search/video?q={keyword.replace(' ', '%20')}"
    print(f"Navigating to TikTok search page: {search_url}")

    try:
        driver.get(search_url)
        print(f"Successfully navigated to: {driver.title}") # Check page title

        # Wait for the main content to load (e.g., a video card)
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-e2e="search-card-container"]'))
        )
        print("TikTok search page loaded.")

        # --- Handle potential consent pop-ups (TikTok often shows these) ---
        # This is a generic attempt; specific selectors might be needed over time.
        try:
            # Look for a button that accepts cookies or dismisses a banner
            consent_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accept all') or contains(., 'Continue')]"))
            )
            consent_button.click()
            print("Attempted to click consent button.")
            time.sleep(2) # Give time for the banner to disappear
        except:
            print("No consent pop-up found or clickable within timeout.")
        # --- End consent pop-up handling ---


        # --- Scroll to load more videos ---
        print("Scrolling to load more videos (up to 3 times)...")
        for _ in range(3): # Scroll a few times to get more videos
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3) # Give time for new content to load

        # --- Collect Video Links ---
        print("Collecting video links from the search results...")
        video_links = set() # Use a set to store unique links
        video_elements = driver.find_elements(By.CSS_SELECTOR, 'div[data-e2e="search-card-container"] a')
        for element in video_elements:
            href = element.get_attribute('href')
            if href and "/video/" in href:
                video_links.add(href)
        print(f"Found {len(video_links)} unique video links.")

        downloaded_count = 0
        for i, video_page_url in enumerate(list(video_links)):
            if downloaded_count >= num_videos:
                print(f"Reached desired number of videos ({num_videos}). Stopping.")
                break

            print(f"\n--- Processing video {i+1}/{len(video_links)}: {video_page_url} ---")
            try:
                driver.get(video_page_url)
                WebDriverWait(driver, 20).until(
                    EC.presence_of_element_located((By.TAG_NAME, 'video'))
                )
                time.sleep(2)
                video_element = driver.find_element(By.TAG_NAME, 'video')
                video_src = video_element.get_attribute('src')

                if video_src:
                    print(f"Found video source URL: {video_src}")
                    filename = f"{mb_util.snake_case(keyword)}_{time.time_ns()}.mp4"
                    filepath = os.path.join(output_dir, filename)
                    print(f"Downloading video to: {filepath}")
                    response = requests.get(video_src, stream=True)
                    response.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print(f"Successfully downloaded: {filename}")
                    downloaded_count += 1
                else:
                    print("Could not find video source URL on this page.")
            except Exception as e:
                print(f"Error processing video page {video_page_url}: {e}")
                continue
    except Exception as e:
        print(f"An unexpected error occurred during the process: {e}")
    finally:
        if 'driver' in locals() and driver:
            print("\nClosing WebDriver...")
            driver.quit()
        print("Script finished.")

# --- How to use the script ---
if __name__ == "__main__":
    search_keyword = input("Enter the keyword to search for TikTok videos: ")
    num_videos_to_download = int(input("Enter the number of videos to download (e.g., 5): "))
    actual_output_dir = f"./tmp/tiktok/{mb_util.snake_case(search_keyword)}"
    download_tiktok_videos_by_keyword(search_keyword, num_videos_to_download, output_dir=actual_output_dir)
    print(f"\nVideos for '{search_keyword}' are being downloaded to the '{actual_output_dir}' folder.")