from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import threading

# Request usernames from the user
instagram_username = input("Enter Instagram username: ")
tiktok_username = input("Enter TikTok username: ")

def add_click_animation(driver):
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

def click_button_and_point(driver, button_text, x, y):
    driver.execute_script(f"""
    let button = Array.from(document.querySelectorAll('p.fc-button-label'))
                      .find(el => el.textContent.trim() === '{button_text}');
    if (button) {{
        let rect = button.getBoundingClientRect();
        let centerX = rect.left + rect.width / 2;
        let centerY = rect.top + rect.height / 2;

        let circle = document.getElementById('click-animation');
        circle.style.left = (centerX - 15) + 'px';
        circle.style.top = (centerY - 15) + 'px';
        circle.style.transform = 'scale(1.5)';
        setTimeout(() => {{ circle.style.transform = 'scale(1)'; }}, 100);

        button.focus();
        button.click();
    }}

    let circle = document.getElementById('click-animation');
    circle.style.left = '{x - 15}px';
    circle.style.top = '{y - 15}px';
    circle.style.transform = 'scale(1.5)';
    setTimeout(() => {{ circle.style.transform = 'scale(1)'; }}, 100);

    let elem = document.elementFromPoint({x}, {y});
    if (elem) {{
        elem.focus();
        elem.click();
    }}
    """)

def open_anonyig(username):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://anonyig.com")
    time.sleep(3)  # Ждем загрузки страницы

    add_click_animation(driver)
    time.sleep(1)
    click_button_and_point(driver, "Отказаться", 100, 270)
    time.sleep(0.5)

    active_element = driver.switch_to.active_element
    active_element.send_keys(username)
    active_element.send_keys(Keys.RETURN)

    time.sleep(300)
    driver.quit()

def open_snaptik(username):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://snaptik.kim/ru/tiktok-story-viewer/")
    time.sleep(3)

    add_click_animation(driver)
    time.sleep(1)
    click_button_and_point(driver, "Do not consent", 140, 280)
    time.sleep(0.5)

    active_element = driver.switch_to.active_element
    active_element.send_keys(username)
    active_element.send_keys(Keys.RETURN)

    time.sleep(300)
    driver.quit()

# Запуск обоих сайтов параллельно
thread1 = threading.Thread(target=open_anonyig, args=(instagram_username,))
thread2 = threading.Thread(target=open_snaptik, args=(tiktok_username,))

thread1.start()
thread2.start()

thread1.join()
thread2.join()
