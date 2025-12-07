from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Chrome driver setup
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

try:
    driver.get("https://anonyig.com")
    time.sleep(3)  # wait for the page to load

    # Create an ActionChains object to control mouse and keyboard
    actions = ActionChains(driver)

    x_coord = 500  # example: X coordinate
    y_coord = 300  # example: Y coordinate

    # Move the mouse to the coordinates and click
    actions.move_by_offset(x_coord, y_coord).click().perform()
    time.sleep(1)  # small timeout after click

    # Enter text
    actions.send_keys("cristiano").send_keys(Keys.RETURN).perform()

    time.sleep(60)  # wait for results

finally:
    driver.quit()
