from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading

def open_anonyig():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://anonyig.com")
    time.sleep(3)  # wait for page to load

    # Add click animation
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

    second_x = 100
    second_y = 270

    time.sleep(1)

    # Click "Отказаться"
    driver.execute_script("""
    let button = Array.from(document.querySelectorAll('p.fc-button-label'))
                      .find(el => el.textContent.trim() === 'Отказаться');
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

    time.sleep(0.5)

    active_element = driver.switch_to.active_element
    active_element.send_keys("cristiano")
    active_element.send_keys(Keys.RETURN)

    time.sleep(300)
    driver.quit()


def open_snaptik():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://snaptik.kim/ru/tiktok-story-viewer/")
    time.sleep(3)

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

    second_x = 140
    second_y = 280

    time.sleep(1)

    # Click "Do not consent"
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

    time.sleep(0.5)

    active_element = driver.switch_to.active_element
    active_element.send_keys("cristiano")
    active_element.send_keys(Keys.RETURN)

    time.sleep(300)
    driver.quit()


# Run both functions in parallel
thread1 = threading.Thread(target=open_anonyig)
thread2 = threading.Thread(target=open_snaptik)

thread1.start()
thread2.start()

thread1.join()
thread2.join()
