import os
import re
import requests
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

# States for ConversationHandler
WAITING_USERNAME = 1
ASKING_CONTINUE = 2

# Bot token (get from @BotFather)
BOT_TOKEN = "token"


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

        import time
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


def get_main_menu():
    """
    Returns main menu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("TikTok", callback_data='tiktok')],
        [InlineKeyboardButton("Instagram", callback_data='instagram')]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_tiktok_menu():
    """
    Returns TikTok submenu keyboard
    """
    keyboard = [
        [InlineKeyboardButton("Get Avatar", callback_data='tiktok_avatar')],
        [InlineKeyboardButton("View Stories", callback_data='tiktok_stories')],
        [InlineKeyboardButton("View Reposts", callback_data='tiktok_reposts')],
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
        "Fully anonymous spy tool powered by OSINT\n\n"
        "Select platform:"
    )

    await update.message.reply_text(
        welcome_text,
        reply_markup=get_main_menu()
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
            "Select action:",
            reply_markup=get_tiktok_menu()
        )
        return ConversationHandler.END

    elif query.data == 'instagram':
        await query.edit_message_text(
            "Instagram module coming soon.\n\n"
            "Use /start to return to menu."
        )
        return ConversationHandler.END

    elif query.data == 'back_main':
        welcome_text = (
            "█▀ █▀█ █▄█   ▀█▀ █▀█ █▀█ █░░\n"
            "▄█ █▀▀ ░█░   ░█░ █▄█ █▄█ █▄▄\n\n"
            "Fully anonymous spy tool powered by OSINT\n\n"
            "Select platform:"
        )
        await query.edit_message_text(
            welcome_text,
            reply_markup=get_main_menu()
        )
        return ConversationHandler.END

    elif query.data == 'tiktok_avatar':
        await query.edit_message_text(
            "Enter target username (without @):"
        )
        return WAITING_USERNAME

    elif query.data in ['tiktok_stories', 'tiktok_reposts']:
        await query.edit_message_text(
            "This feature is coming soon.\n\n"
            "Use /start to return to menu."
        )
        return ConversationHandler.END

    elif query.data == 'continue_yes':
        welcome_text = (
            "█▀ █▀█ █▄█   ▀█▀ █▀█ █▀█ █░░\n"
            "▄█ █▀▀ ░█░   ░█░ █▄█ █▄█ █▄▄\n\n"
            "Fully anonymous spy tool powered by OSINT\n\n"
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


async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Receives username and parses avatar
    """
    username = update.message.text.strip().lstrip('@')

    if not username:
        await update.message.reply_text(
            "Invalid username.\n"
            "Try again or use /start"
        )
        return WAITING_USERNAME

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
            WAITING_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, receive_username)
            ]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    # Add handlers
    application.add_handler(conv_handler)

    # Start bot
    print("Bot is running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
