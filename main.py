from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# -------------------------------
# Chrome driver setup
# -------------------------------
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://anonyig.com")
time.sleep(3)  # wait for the page to load

# -------------------------------
# Add a red circle for click animation
# -------------------------------
driver.execute_script("""
if (!document.getElementById('click-animation')) {
    let circle = document.createElement('div');
    circle.id = 'click-animation';
    circle.style.position = 'absolute';
    circle.style.width = '30px';
    circle.style.height = '30px';
    circle.style.border = '3px solid red';
    circle.style.borderRadius = '50%';
    circle.style.pointerEvents = 'none';
    circle.style.transition = 'all 0.2s ease';
    circle.style.zIndex = 9999;
    document.body.appendChild(circle);
}
""")

# -------------------------------
# Coordinates for the click
# -------------------------------
x_coord = 100  # X coordinate
y_coord = 270  # Y coordinate

# -------------------------------
# Animate and click the input element
# -------------------------------
driver.execute_script(f"""
let circle = document.getElementById('click-animation');
// Move circle to click position and animate
circle.style.left = '{x_coord - 15}px';
circle.style.top = '{y_coord - 15}px';
circle.style.transform = 'scale(1.5)';
setTimeout(() => {{ circle.style.transform = 'scale(1)'; }}, 100);

// Find the element under the coordinates
let elem = document.elementFromPoint({x_coord}, {y_coord});
if (elem) {{
    elem.focus();             // Ensure input is focused
    elem.click();             // Trigger click event
}}
""")

time.sleep(0.5)  # wait for the input to gain focus

# -------------------------------
# Type "cristiano" in the input field
# -------------------------------
active_element = driver.switch_to.active_element
active_element.send_keys("cristiano")
active_element.send_keys(Keys.RETURN)  # press Enter to submit

time.sleep(60)  # wait to see the result

# -------------------------------
# Close the browser
# -------------------------------
driver.quit()
