from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re
import requests
import os


def get_avatar_url(username):
    """
    Gets avatar URL from TikTok profile in hidden mode
    """
    # Chrome setup in headless mode (hidden) with speed optimizations
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-images')
    chrome_options.add_argument('--disable-javascript')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-infobars')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    chrome_options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(options=chrome_options)

    avatar_url = None

    try:
        # Build profile URL
        profile_url = f"https://www.tiktok.com/@{username}"
        print(f"Opening profile in background: {profile_url}")

        # Open profile page
        driver.get(profile_url)

        # Wait minimal time for HTML to load
        time.sleep(2)

        # Get page HTML source
        page_source = driver.page_source

        # Search for avatar link using regex
        # Pattern to find img with css-10s4roi class or similar
        pattern = r'<img[^>]*class="[^"]*ImgAvatar[^"]*"[^>]*src="([^"]+)"[^>]*>'
        matches = re.findall(pattern, page_source)

        if not matches:
            # Try alternative pattern
            pattern = r'src="([^"]+)"[^>]*class="[^"]*ImgAvatar[^"]*"'
            matches = re.findall(pattern, page_source)

        if matches:
            avatar_url = matches[0]
            print(f"Found avatar link: {avatar_url}")
        else:
            print("Could not find avatar link in page source.")
            print("Page structure may have changed or profile did not load.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        driver.quit()

    return avatar_url


def download_avatar(avatar_url, username):
    """
    Downloads avatar to Downloads folder
    """
    try:
        # Get Downloads folder path
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')

        # Create filename
        filename = f"tiktok_avatar_{username}.jpg"
        filepath = os.path.join(downloads_path, filename)

        print(f"\nDownloading avatar...")

        # Download image
        response = requests.get(avatar_url, stream=True)
        response.raise_for_status()

        # Save to file
        with open(filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        print(f"Avatar downloaded to Downloads: {filename}")

    except Exception as e:
        print(f"Error downloading avatar: {e}")


def view_avatar(avatar_url):
    """
    Opens avatar in visible browser
    """
    print("\nOpening avatar in browser...")

    # Create new visible browser
    visible_options = Options()
    visible_driver = webdriver.Chrome(options=visible_options)

    # Set window size to half screen
    screen_width = visible_driver.execute_script("return window.screen.width;")
    screen_height = visible_driver.execute_script("return window.screen.height;")
    visible_driver.set_window_size(screen_width // 2, screen_height)
    visible_driver.set_window_position(0, 0)

    # Open avatar
    visible_driver.get(avatar_url)
    print("Avatar opened!")

    # Wait so user can see the result
    print("\nPress Enter in console to close browser...")
    input()

    visible_driver.quit()
    print("Browser closed.")


def main():
    print("=== TikTok Avatar Parser ===\n")

    # Ask for username
    username = input("Enter TikTok username (without @): ").strip()

    if not username:
        print("Username cannot be empty!")
        return

    # Remove @ if user entered it
    username = username.lstrip('@')

    # Ask what to do
    print("\nWhat do you want to do?")
    print("1. View avatar in browser")
    print("2. Download avatar")
    choice = input("Enter your choice (1 or 2): ").strip()

    if choice not in ['1', '2']:
        print("Invalid choice! Please enter 1 or 2.")
        return

    print(f"\nSearching avatar for user: @{username}\n")

    # Get avatar URL
    avatar_url = get_avatar_url(username)

    if not avatar_url:
        print("Avatar not found. Exiting.")
        return

    # Execute based on choice
    if choice == '1':
        view_avatar(avatar_url)
    else:
        download_avatar(avatar_url, username)


if __name__ == "__main__":
    main()
