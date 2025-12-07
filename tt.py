from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time

# Chrome driver setup
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
driver.get("https://snaptik.kim/ru/tiktok-story-viewer/")
time.sleep(3)  # wait for the page to fully load

# Add a red circle for click animation
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

# Coordinates for second click + input
second_x = 140
second_y = 280

# Step 0: Wait 1 second after page load
time.sleep(1)

# Step 1: Find "Do not consent" button and click it 3 times
for _ in range(1):
    driver.execute_script("""
    let button = Array.from(document.querySelectorAll('p.fc-button-label'))
                      .find(el => el.textContent.trim() === 'Do not consent');
    if (button) {
        let rect = button.getBoundingClientRect();
        let centerX = rect.left + rect.width / 2;
        let centerY = rect.top + rect.height / 2;

        let circle = document.getElementById('click-animation');
        circle.style.left = (centerX - 15) + 'px';
        circle.style.top = (centerY - 15) + 'px';
        circle.style.transform = 'scale(1.5)';
        setTimeout(() => { circle.style.transform = 'scale(1)'; }, 100);

        button.focus();
        button.click();
    }
    """)

# Step 2: Wait 2 seconds, then click second coordinates + input
time.sleep(0.1)

driver.execute_script(f"""
let circle = document.getElementById('click-animation');
circle.style.left = '{second_x - 15}px';
circle.style.top = '{second_y - 15}px';
circle.style.transform = 'scale(1.5)';
setTimeout(() => {{ circle.style.transform = 'scale(1)'; }}, 100);

let elem = document.elementFromPoint({second_x}, {second_y});
if (elem) {{
    elem.focus();
    elem.click();
}}
""")

time.sleep(0.5)  # wait for the input to gain focus

# Step 3: Type "cristiano" in the input field
active_element = driver.switch_to.active_element
active_element.send_keys("cristiano")
active_element.send_keys(Keys.RETURN)  # press Enter to submit

time.sleep(300)  # wait to see the result

# Close the browser
driver.quit()
