import os
import re
import requests
import tempfile
import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    ApplicationHandlerStop
)

# States for ConversationHandler
WAITING_USERNAME_AVATAR = 1
WAITING_USERNAME_STORIES = 2
ASKING_CONTINUE = 3
WAITING_SPOTIFY_USER_LINK = 4
WAITING_SPOTIFY_PLAYLIST_LINK = 5
WAITING_INSTAGRAM_USERNAME = 6

BOT_TOKEN = "token"

STORY_CLICK_X = 760
STORY_CLICK_Y = 276

STORY_CLICK_X_2 = 275
STORY_CLICK_Y_2 = 25

# Duration settings
WINDOW_OPEN_DURATION = 1
CLICK_INDICATOR_DURATION = 1


def get_tiktok_avatar_url(username):
    """
    Gets avatar URL from TikTok profile
    """
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
        profile_url = f"https://www.tiktok.com/@{username}"
        driver.get(profile_url)

        time.sleep(2)

        page_source = driver.page_source

        # Pattern 1: search for img with ImgAvatar
        pattern1 = r'<img[^>]*class="[^"]*ImgAvatar[^"]*"[^>]*src="([^"]+)"[^>]*>'
        matches = re.findall(pattern1, page_source)

        if not matches:
            pattern1_alt = r'src="([^"]+)"[^>]*class="[^"]*ImgAvatar[^"]*"'
            matches = re.findall(pattern1_alt, page_source)

        if matches:
            avatar_url = matches[0]
        else:
            # Pattern 2: for users with stories
            pattern2 = r'<img[^>]*class="[^"]*TUXBaseAvatar-src[^"]*user-avatar[^"]*"[^>]*src="([^"]+)"[^>]*>'
            matches = re.findall(pattern2, page_source)

            if not matches:
                pattern2_alt = r'src="([^"]+)"[^>]*class="[^"]*TUXBaseAvatar-src[^"]*user-avatar[^"]*"'
                matches = re.findall(pattern2_alt, page_source)

            if matches:
                avatar_url = matches[0]

    except Exception as e:
        print(f"Error getting avatar: {e}")
    finally:
        driver.quit()

    return avatar_url


def get_tiktok_stories(username):
    """
    Gets story video URLs from TikTok profile
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    # Don't use headless mode for clicking

    driver = webdriver.Chrome(options=chrome_options)
    video_urls = []

    try:
        profile_url = f"https://www.tiktok.com/@{username}"
        print(f"Opening profile: {profile_url}")
        driver.get(profile_url)

        time.sleep(3)

        # Function to show red circle at click position
        def show_click_indicator(x, y):
            js_code = f"""
            var circle = document.createElement('div');
            circle.style.position = 'fixed';
            circle.style.left = '{x}px';
            circle.style.top = '{y}px';
            circle.style.width = '20px';
            circle.style.height = '20px';
            circle.style.borderRadius = '50%';
            circle.style.backgroundColor = 'red';
            circle.style.zIndex = '999999';
            circle.style.pointerEvents = 'none';
            circle.style.transform = 'translate(-50%, -50%)';
            document.body.appendChild(circle);
            setTimeout(function() {{
                circle.remove();
            }}, {CLICK_INDICATOR_DURATION * 1000});
            """
            driver.execute_script(js_code)

        # First click
        print(f"First click on coordinates: ({STORY_CLICK_X}, {STORY_CLICK_Y})")
        show_click_indicator(STORY_CLICK_X, STORY_CLICK_Y)
        actions = ActionChains(driver)
        actions.move_by_offset(STORY_CLICK_X, STORY_CLICK_Y).click().perform()

        time.sleep(2)

        # Reset mouse position for second click
        actions = ActionChains(driver)
        actions.move_by_offset(-STORY_CLICK_X, -STORY_CLICK_Y).perform()

        # Second click
        print(f"Second click on coordinates: ({STORY_CLICK_X_2}, {STORY_CLICK_Y_2})")
        show_click_indicator(STORY_CLICK_X_2, STORY_CLICK_Y_2)
        actions = ActionChains(driver)
        actions.move_by_offset(STORY_CLICK_X_2, STORY_CLICK_Y_2).click().perform()

        time.sleep(3)

        # Get page source after clicking
        page_source = driver.page_source

        # Search for video element with specific pattern
        # Pattern for video with crossorigin="use-credentials"
        pattern = r'<video[^>]*crossorigin="use-credentials"[^>]*src="([^"]+)"[^>]*>'
        matches = re.findall(pattern, page_source)

        if not matches:
            # Alternative pattern - src first
            pattern_alt = r'src="([^"]+)"[^>]*crossorigin="use-credentials"'
            matches = re.findall(pattern_alt, page_source)

        if not matches:
            # Try to find any video element with src
            pattern_fallback = r'<video[^>]*src="([^"]+)"[^>]*>'
            matches = re.findall(pattern_fallback, page_source)

        if matches:
            video_urls = matches
            print(f"Found {len(video_urls)} story video(s)")
        else:
            print("No stories found in page source")

        # Keep window open for specified duration
        print(f"Keeping window open for {WINDOW_OPEN_DURATION} seconds...")
        time.sleep(WINDOW_OPEN_DURATION)

    except Exception as e:
        print(f"Error getting stories: {e}")
    finally:
        driver.quit()

    return video_urls


def get_instagram_avatar_url(username):
    """
    Gets avatar URL from Instagram profile
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(options=chrome_options)
    avatar_url = None

    try:
        profile_url = f"https://www.instagram.com/{username}"
        print(f"Opening Instagram profile: {profile_url}")
        driver.get(profile_url)

        time.sleep(3)

        # Remove the blocking div
        js_code = """
        var blockingDiv = document.querySelector('div.x1n2onr6.xzkaem6');
        if (blockingDiv) {
            blockingDiv.remove();
        }
        """
        driver.execute_script(js_code)

        time.sleep(1)

        page_source = driver.page_source

        # Search for the avatar img inside span element
        pattern = r'<meta property="og:image" content="([^"]+)"'
        matches = re.findall(pattern, page_source, re.DOTALL)

        if matches:
            avatar_url = matches[0]
            print(f"Found Instagram avatar: {avatar_url}")
        else:
            # Try alternative pattern - search for img with specific classes
            pattern_alt = r'<img[^>]*class="[^"]*xpdipgo x972fbf[^"]*"[^>]*src="([^"]+)"[^>]*>'
            matches = re.findall(pattern_alt, page_source)
            if matches:
                avatar_url = matches[0]
                print(f"Found Instagram avatar (alt): {avatar_url}")
            else:
                print("Instagram avatar not found in page source")

    except Exception as e:
        print(f"Error getting Instagram avatar: {e}")
    finally:
        driver.quit()

    return avatar_url


def get_spotify_image_url(url):
    """
    Gets image URL from Spotify user profile or playlist
    """
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-notifications')
    chrome_options.add_argument('--disable-popup-blocking')
    chrome_options.page_load_strategy = 'eager'

    driver = webdriver.Chrome(options=chrome_options)
    image_url = None

    try:
        print(f"Opening Spotify URL: {url}")
        driver.get(url)

        time.sleep(3)

        page_source = driver.page_source

        # Search for div with specific classes containing img
        pattern = r'<div class="bFtVZZnZgTWjjyzkPA5k"[^>]*>.*?<img[^>]*src="([^"]+)"[^>]*class="[^"]*LBM25IAoFtd0wh7k3EGM[^"]*"[^>]*>.*?</div>'
        matches = re.findall(pattern, page_source, re.DOTALL)

        if not matches:
            # Alternative pattern - try to find img with specific classes
            pattern_alt = r'<img[^>]*class="[^"]*LBM25IAoFtd0wh7k3EGM bFtVZZnZgTWjjyzkPA5k[^"]*"[^>]*src="([^"]+)"[^>]*>'
            matches = re.findall(pattern_alt, page_source)

        if not matches:
            # Another alternative - src first
            pattern_alt2 = r'<img[^>]*src="([^"]+)"[^>]*class="[^"]*LBM25IAoFtd0wh7k3EGM bFtVZZnZgTWjjyzkPA5k[^"]*"[^>]*>'
            matches = re.findall(pattern_alt2, page_source)

        if matches:
            image_url = matches[0]
            print(f"Found image URL: {image_url}")
        else:
            print("Image not found in page source")

    except Exception as e:
        print(f"Error getting Spotify image: {e}")
    finally:
        driver.quit()

    return image_url


def download_avatar_to_temp(avatar_url):
    """
    Downloads avatar to temporary file
    """
    try:
        response = requests.get(avatar_url, stream=True, timeout=10)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')

        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)

        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"Error downloading: {e}")
        return None


def download_video_to_temp(video_url):
    """
    Downloads video to temporary file
    """
    try:
        response = requests.get(video_url, stream=True, timeout=30)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')

        for chunk in response.iter_content(chunk_size=8192):
            temp_file.write(chunk)

        temp_file.close()
        return temp_file.name
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None


def get_main_menu():
    """
    Returns main menu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("TikTok", callback_data='tiktok')],
        [InlineKeyboardButton("Instagram", callback_data='instagram')],
        [InlineKeyboardButton("Spotify", callback_data='spotify')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_tiktok_menu():
    """
    Returns TikTok submenu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("Get Avatar", callback_data='tiktok_avatar')],
        [InlineKeyboardButton("View Stories (beta)", callback_data='tiktok_stories')],
        [InlineKeyboardButton("View Reposts (coming soon...)", callback_data='tiktok_reposts')],
        [InlineKeyboardButton("← Back", callback_data='back_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_instagram_menu():
    """
    Returns Instagram submenu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("Get Avatar (beta)", callback_data='instagram_avatar')],
        [InlineKeyboardButton("View Stories (coming soon...)", callback_data='instagram_stories')],
        [InlineKeyboardButton("Download full profile (coming soon...)", callback_data='instagram_full_profile')],
        [InlineKeyboardButton("← Back", callback_data='back_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_spotify_menu():
    """
    Returns Spotify submenu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("Get User Avatar", callback_data='spotify_user_avatar')],
        [InlineKeyboardButton("Get Playlist Cover", callback_data='spotify_playlist_cover')],
        [InlineKeyboardButton("← Back", callback_data='back_main')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_continue_menu():
    """
    Returns continue menu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("Yes", callback_data='continue_yes')],
        [InlineKeyboardButton("No", callback_data='continue_no')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for /start command - shows welcome message
    """
    welcome_text = (
        "smSpy\n\n"
        "FULLY ANONYMOUS SPY TOOL\n"
        "Powered by OSINT\n\n"
        "<i>Disclaimer: The developer takes no responsibility for any actions performed using this tool. You use it entirely at your own risk. The developer assumes no liability whatsoever use it wisely.</i>\n\n"
        "Select platform:"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu(),
        parse_mode='HTML'
    )
    return ConversationHandler.END


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handler for button presses
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'tiktok':
        await query.edit_message_text(
            "TikTok OSINT\n\n"
            "If you have trouble accessing stories, you can visit <a href='https://is.gd/LisZbE'>this site</a> to view them from there.\n\n"
            "<i>(Your IP address may be blocked if you make repeated attempts to access this resource or if you are using Tor browser.)</i>\n\n"
            "Select action:",
            reply_markup=get_tiktok_menu(),
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        return ConversationHandler.END


    elif query.data == 'instagram':
        await query.edit_message_text(
            "Instagram OSINT\n\n"
            "️Note: Instagram actively blocks this type of activity due to frequent automated requests, so some features may work unstably or stop working temporarily.\n\n"
            "If you keep encountering errors, you can visit <a href='https://is.gd/NPa9hj'>this site</a> to use Instagram OSINT from there.\n\n"
            "Select action:",
            reply_markup=get_instagram_menu(),
            parse_mode='HTML',
            disable_web_page_preview=True
        )
        return ConversationHandler.END

    elif query.data == 'spotify':
        await query.edit_message_text(
            "Spotify OSINT\n\n"
            "Select action:",
            reply_markup=get_spotify_menu()
        )
        return ConversationHandler.END

    elif query.data == 'back_main':
        welcome_text = (
            "smSpy\n\n"
            "FULLY ANONYMOUS SPY TOOL\n"
            "Powered by OSINT\n\n"
            "<i>Disclaimer: The developer takes no responsibility for any actions performed using this tool. You use it entirely at your own risk. The developer assumes no liability whatsoever use it wisely.</i>\n\n"
            "Select platform:"
        )
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu(),
            parse_mode='HTML'
        )
        return ConversationHandler.END

    elif query.data == 'tiktok_avatar':
        await query.edit_message_text(
            "Enter target username (without @):"
        )
        return WAITING_USERNAME_AVATAR

    elif query.data == 'tiktok_stories':
        await query.edit_message_text(
            "Enter target username (without @):"
        )
        return WAITING_USERNAME_STORIES

    elif query.data == 'tiktok_reposts':
        await query.edit_message_text(
            "This feature is coming soon.\n\n"
            "Use /start to return to menu."
        )
        return ConversationHandler.END

    elif query.data == 'instagram_avatar':
        await query.edit_message_text(
            "Enter target username (without @):"
        )
        return WAITING_INSTAGRAM_USERNAME

    elif query.data == 'instagram_stories':
        await query.edit_message_text(
            "This feature is coming soon.\n\n"
            "Use /start to return to menu."
        )
        return ConversationHandler.END

    elif query.data == 'instagram_full_profile':
        await query.edit_message_text(
            "This feature is coming soon.\n\n"
            "Use /start to return to menu."
        )
        return ConversationHandler.END

    elif query.data == 'spotify_user_avatar':
        await query.edit_message_text(
            "Send Spotify user profile link\n"
            "Format: https://open.spotify.com/user/x"
        )
        return WAITING_SPOTIFY_USER_LINK

    elif query.data == 'spotify_playlist_cover':
        await query.edit_message_text(
            "Send Spotify playlist link\n"
            "Format: https://open.spotify.com/playlist/x"
        )
        return WAITING_SPOTIFY_PLAYLIST_LINK

    elif query.data == 'continue_yes':
        welcome_text = (
            "smSpy\n\n"
            "FULLY ANONYMOUS SPY TOOL\n"
            "Powered by OSINT\n\n"
            "<i>Disclaimer: The developer takes no responsibility for any actions performed using this tool. You use it entirely at your own risk. The developer assumes no liability whatsoever use it wisely.</i>\n\n"
            "Select platform:"
        )
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END

    elif query.data == 'continue_no':
        await query.edit_message_text(
            "Session terminated.\n\n"
            "Use /start to begin new session."
        )
        return ConversationHandler.END


def check_special_trigger(text: str):
    if not text:
        return None

    triggers_a = {
        "user374950291619494",
        "566c6164696d6972",
        "https://open.spotify.com/user/31zvkrndb5bz4pvpckrjigpjpu7a"
    }
    responses_a = [
        "Haha, yeah… no. 👌",
        "No no no, nice try though. 😉",
        "I’ll pretend I didn’t see that 🙈🙈",
        "🤫🧏‍♂️"
    ]

    if any(trigger in text for trigger in triggers_a):
        return random.choice(responses_a)

    triggers_b = {
        "issabelsp",
        "issabelsp_",
        "https://open.spotify.com/user/uk6ha88ro4nqbnt2yg62v35aq"
    }
    responses_b = [
        "Forget about it. 🫶",
        "Request denied. 🛑",
        "Let’s not do that, shall we? 😊",
        "️👀👀👀"
    ]

    if any(trigger in text for trigger in triggers_b):
        return random.choice(responses_b)

    triggers_c = {
        "https://open.spotify.com/playlist/0ZPMdghTbUd581jVMOheN2",
        "https://open.spotify.com/playlist/0kd06bVcrfAmZWSX0MYH44",
        "https://open.spotify.com/playlist/0zPksXId0xPjfOgumuFOOf",
        "https://open.spotify.com/playlist/1Ex0CRvsnzdimLR58QNcUY",
        "https://open.spotify.com/playlist/0awAcyx4fUYglI36Xtnpmw",
        "https://open.spotify.com/playlist/7B0zVStcrElJMyKxo8YzJg"
    }
    responses_c = [
        "Seems like this content is out of reach. 🤷‍♂️",
        "Access denied… try something else. ✌️😘",
        "Seems like the universe says no to this one. 🫥"
    ]

    if any(trigger in text for trigger in triggers_c):
        return random.choice(responses_c)

    return None


async def receive_username_avatar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives username and parses avatar
    """
    username = update.message.text.strip().lstrip('@')

    if not username:
        await update.message.reply_text(
            "Invalid username.\n"
            "Try again or use /start"
        )
        return WAITING_USERNAME_AVATAR

    # Send search status
    status_message = await update.message.reply_text(
        f"Scanning target: @{username}\n"
        "Please wait..."
    )

    try:
        # Get avatar URL
        avatar_url = get_tiktok_avatar_url(username)

        if not avatar_url:
            await status_message.edit_text(
                f"Target not found: @{username}\n\n"
                "Possible reasons:\n"
                "• Invalid username\n"
                "• Private profile\n"
                "• Profile does not exist\n\n"
                "Use /start for new session."
            )
            return ConversationHandler.END

        await status_message.edit_text("Extracting data...")

        # Download avatar
        avatar_path = download_avatar_to_temp(avatar_url)

        if not avatar_path:
            await status_message.edit_text(
                "Failed to extract avatar.\n"
                "Try again later or use /start"
            )
            return ConversationHandler.END

        # Send avatar
        await status_message.edit_text("Sending data...")

        with open(avatar_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"Target: @{username}\nData type: Avatar"
            )

        # Delete status message
        await status_message.delete()

        # Delete temporary file
        os.unlink(avatar_path)

        # Ask if user wants to continue
        await update.message.reply_text(
            "Do you want to continue?",
            reply_markup=get_continue_menu()
        )

    except Exception as e:
        await status_message.edit_text(
            f"Error occurred: {str(e)}\n\n"
            "Try again later or use /start"
        )
        print(f"Error: {e}")

    return ConversationHandler.END


async def receive_username_stories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives username and parses stories
    """
    username = update.message.text.strip().lstrip('@')

    if not username:
        await update.message.reply_text(
            "Invalid username.\n"
            "Try again or use /start"
        )
        return WAITING_USERNAME_STORIES

    # Send search status
    status_message = await update.message.reply_text(
        f"Scanning target: @{username}\n"
        "Extracting stories... This may take a moment."
    )

    try:
        # Get story video URLs
        video_urls = get_tiktok_stories(username)

        if not video_urls:
            await status_message.edit_text(
                f"No stories found for: @{username}\n\n"
                "Possible reasons:\n"
                "• No active stories\n"
                "• Private profile\n"
                "• Stories expired\n\n"
                "Use /start for new session."
            )
            return ConversationHandler.END

        await status_message.edit_text(f"Found {len(video_urls)} story/stories. Downloading...")

        # Download and send each video
        for idx, video_url in enumerate(video_urls, 1):
            video_path = download_video_to_temp(video_url)

            if not video_path:
                await update.message.reply_text(f"Failed to download story {idx}")
                continue

            # Send video
            with open(video_path, 'rb') as video:
                await update.message.reply_video(
                    video=video,
                    caption=f"Target: @{username}\nStory {idx}/{len(video_urls)}"
                )

            # Delete temporary file
            os.unlink(video_path)

        # Delete status message
        await status_message.delete()

        # Ask if user wants to continue
        await update.message.reply_text(
            "Do you want to continue?",
            reply_markup=get_continue_menu()
        )

    except Exception as e:
        await status_message.edit_text(
            f"Error occurred: {str(e)}\n\n"
            "Try again later or use /start"
        )
        print(f"Error: {e}")

    return ConversationHandler.END


async def receive_instagram_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives Instagram username and parses avatar
    """
    username = update.message.text.strip().lstrip('@')

    if not username:
        await update.message.reply_text(
            "Invalid username.\n"
            "Try again or use /start"
        )
        return WAITING_INSTAGRAM_USERNAME

    # Send search status
    status_message = await update.message.reply_text(
        f"Scanning target: @{username}\n"
        "Please wait..."
    )

    try:
        # Get avatar URL
        avatar_url = get_instagram_avatar_url(username)

        if not avatar_url:
            await status_message.edit_text(
                f"Target not found: @{username}\n\n"
                "Possible reasons:\n"
                "• Invalid username\n"
                "• Private profile\n"
                "• Profile does not exist\n\n"
                "Use /start for new session."
            )
            return ConversationHandler.END

        await status_message.edit_text("Extracting data...")

        # Download avatar
        avatar_path = download_avatar_to_temp(avatar_url)

        if not avatar_path:
            await status_message.edit_text(
                "Failed to extract avatar.\n"
                "Try again later or use /start"
            )
            return ConversationHandler.END

        # Send avatar
        await status_message.edit_text("Sending data...")

        with open(avatar_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"Target: @{username}\nData type: Avatar"
            )

        # Delete status message
        await status_message.delete()

        # Delete temporary file
        os.unlink(avatar_path)

        # Ask if user wants to continue
        await update.message.reply_text(
            "Do you want to continue?",
            reply_markup=get_continue_menu()
        )

    except Exception as e:
        await status_message.edit_text(
            f"Error occurred: {str(e)}\n\n"
            "Try again later or use /start"
        )
        print(f"Error: {e}")

    return ConversationHandler.END


async def receive_spotify_user_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives Spotify user profile link and extracts avatar
    """
    link = update.message.text.strip()

    # Validate link format
    if not link.startswith("https://open.spotify.com/"):
        await update.message.reply_text(
            "Invalid link format.\n"
            "Expected: https://open.spotify.com/user/x\n\n"
            "Try again or use /start"
        )
        return WAITING_SPOTIFY_USER_LINK

    # Check if user sent playlist link instead
    if "/playlist/" in link:
        await update.message.reply_text(
            "This is a public playlist link.\n"
            "Please send a user profile link.\n\n"
            "Format: https://open.spotify.com/user/x"
        )
        return WAITING_SPOTIFY_USER_LINK

    # Check if it's a user profile link
    if "/user/" not in link:
        await update.message.reply_text(
            "Invalid link format.\n"
            "Expected: https://open.spotify.com/user/x\n\n"
            "Try again or use /start"
        )
        return WAITING_SPOTIFY_USER_LINK

    # Send processing status
    status_message = await update.message.reply_text(
        "Processing Spotify user profile...\n"
        "Please wait..."
    )

    try:
        # Get image URL from Spotify
        image_url = get_spotify_image_url(link)

        if not image_url:
            await status_message.edit_text(
                "Failed to extract user avatar.\n\n"
                "Possible reasons:\n"
                "• Invalid link\n"
                "• Private profile\n"
                "• Profile does not exist\n\n"
                "Use /start for new session."
            )
            return ConversationHandler.END

        await status_message.edit_text("Downloading avatar...")

        # Download image
        image_path = download_avatar_to_temp(image_url)

        if not image_path:
            await status_message.edit_text(
                "Failed to download avatar.\n"
                "Try again later or use /start"
            )
            return ConversationHandler.END

        # Send image
        await status_message.edit_text("Sending data...")

        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"Spotify User Avatar\nSource: {link}"
            )

        # Delete status message
        await status_message.delete()

        # Delete temporary file
        os.unlink(image_path)

        # Ask if user wants to continue
        await update.message.reply_text(
            "Do you want to continue?",
            reply_markup=get_continue_menu()
        )

    except Exception as e:
        await status_message.edit_text(
            f"Error occurred: {str(e)}\n\n"
            "Try again later or use /start"
        )
        print(f"Error: {e}")

    return ConversationHandler.END

async def receive_spotify_playlist_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives Spotify playlist link and extracts cover
    """
    link = update.message.text.strip()

    # Validate link format
    if not link.startswith("https://open.spotify.com/"):
        await update.message.reply_text(
            "Invalid link format.\n"
            "Expected: https://open.spotify.com/playlist/x\n\n"
            "Try again or use /start"
        )
        return WAITING_SPOTIFY_PLAYLIST_LINK

    # Check if user sent user profile link instead
    if "/user/" in link:
        await update.message.reply_text(
            "This is a public profile link.\n"
            "Please send a playlist link.\n\n"
            "Format: https://open.spotify.com/playlist/x"
        )
        return WAITING_SPOTIFY_PLAYLIST_LINK

    # Check if it's a playlist link
    if "/playlist/" not in link:
        await update.message.reply_text(
            "Invalid link format.\n"
            "Expected: https://open.spotify.com/playlist/x\n\n"
            "Try again or use /start"
        )
        return WAITING_SPOTIFY_PLAYLIST_LINK

    # Send processing status
    status_message = await update.message.reply_text(
        "Processing Spotify playlist...\n"
        "Please wait..."
    )

    try:
        # Get image URL from Spotify
        image_url = get_spotify_image_url(link)

        if not image_url:
            await status_message.edit_text(
                "Failed to extract playlist cover.\n\n"
                "Possible reasons:\n"
                "• Invalid link\n"
                "• Private playlist\n"
                "• Playlist does not exist\n\n"
                "Use /start for new session."
            )
            return ConversationHandler.END

        await status_message.edit_text("Downloading cover...")

        # Download image
        image_path = download_avatar_to_temp(image_url)

        if not image_path:
            await status_message.edit_text(
                "Failed to download cover.\n"
                "Try again later or use /start"
            )
            return ConversationHandler.END

        # Send image
        await status_message.edit_text("Sending data...")

        with open(image_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f"Spotify Playlist Cover\nSource: {link}"
            )

        # Delete status message
        await status_message.delete()

        # Delete temporary file
        os.unlink(image_path)

        # Ask if user wants to continue
        await update.message.reply_text(
            "Do you want to continue?",
            reply_markup=get_continue_menu()
        )

    except Exception as e:
        await status_message.edit_text(
            f"Error occurred: {str(e)}\n\n"
            "Try again later or use /start"
        )
        print(f"Error: {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Cancel current operation
    """
    await update.message.reply_text(
        "Operation cancelled.\n"
        "Use /start to return to menu."
    )
    return ConversationHandler.END


def main():
    """
    Start bot
    """
    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler for dialog processing
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            CallbackQueryHandler(button_handler)
        ],
        states={
            WAITING_USERNAME_AVATAR: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username_avatar)
            ],
            WAITING_USERNAME_STORIES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username_stories)
            ],
            WAITING_INSTAGRAM_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_instagram_username)
            ],
            WAITING_SPOTIFY_USER_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_spotify_user_link)
            ],
            WAITING_SPOTIFY_PLAYLIST_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_spotify_playlist_link)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    async def kill_switch_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        response = check_special_trigger(update.message.text)
        if response:
            await update.message.reply_text(response)

            raise ApplicationHandlerStop

    # Add handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, kill_switch_handler),
        group=-1
    )

    application.add_handler(conv_handler, group=0)

    # Start bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
