from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import re


def get_tiktok_avatar(username):
    """
    Opens TikTok profile, finds avatar and opens it in a new tab
    """
    # Chrome setup in headless mode (hidden)
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')

    driver = webdriver.Chrome(options=chrome_options)

    avatar_url = None

    try:
        # Build profile URL
        profile_url = f"https://www.tiktok.com/@{username}"
        print(f"Opening profile in background: {profile_url}")

        # Open profile page
        driver.get(profile_url)

        # Wait for page to load
        time.sleep(5)

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

    # If avatar was found, open it in visible browser
    if avatar_url:
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
    else:
        print("Avatar not found. Browser closed.")


def main():
    print("=== TikTok Avatar Parser ===\n")

    # Ask for username
    username = input("Enter TikTok username (without @): ").strip()

    if not username:
        print("Username cannot be empty!")
        return

    # Remove @ if user entered it
    username = username.lstrip('@')

    print(f"\nSearching avatar for user: @{username}\n")

    # Run parser
    get_tiktok_avatar(username)


if __name__ == "__main__":
    main()