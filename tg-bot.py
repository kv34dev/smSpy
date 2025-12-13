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

WAITING_USERNAME = 1

BOT_TOKEN = "token"


def get_tiktok_avatar_url(username):
    """
    Получает URL аватарки из профиля TikTok
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

        # Паттерн 1: поиск img с ImgAvatar
        pattern1 = r'<img[^>]*class="[^"]*ImgAvatar[^"]*"[^>]*src="([^"]+)"[^>]*>'
        matches = re.findall(pattern1, page_source)

        if not matches:
            pattern1_alt = r'src="([^"]+)"[^>]*class="[^"]*ImgAvatar[^"]*"'
            matches = re.findall(pattern1_alt, page_source)

        if matches:
            avatar_url = matches[0]
        else:
            # Паттерн 2: для пользователей со stories
            pattern2 = r'<img[^>]*class="[^"]*TUXBaseAvatar-src[^"]*user-avatar[^"]*"[^>]*src="([^"]+)"[^>]*>'
            matches = re.findall(pattern2, page_source)

            if not matches:
                pattern2_alt = r'src="([^"]+)"[^>]*class="[^"]*TUXBaseAvatar-src[^"]*user-avatar[^"]*"'
                matches = re.findall(pattern2_alt, page_source)

            if matches:
                avatar_url = matches[0]

    except Exception as e:
        print(f"Ошибка при получении аватарки: {e}")
    finally:
        driver.quit()

    return avatar_url


def download_avatar_to_temp(avatar_url):
    """
    Скачивает аватарку во временный файл
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
        print(f"Ошибка при скачивании: {e}")
        return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик команды /start - показывает главное меню
    """
    keyboard = [
        [InlineKeyboardButton("🎵 TikTok", callback_data='tiktok')],
        [InlineKeyboardButton("📷 Instagram (скоро)", callback_data='instagram')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        '👋 Привет! Я помогу тебе получить аватарку из TikTok или Instagram.\n\n'
        'Выбери платформу:',
        reply_markup=reply_markup
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Обработчик нажатий на кнопки
    """
    query = update.callback_query
    await query.answer()

    if query.data == 'tiktok':
        await query.edit_message_text(
            '🎵 Введите username пользователя TikTok (без @):\n\n'
            'Например: khabib_nurmagomedov'
        )
        return WAITING_USERNAME

    elif query.data == 'instagram':
        await query.edit_message_text(
            '📷 Instagram функционал находится в разработке.\n\n'
            'Используйте /start для возврата в меню.'
        )
        return ConversationHandler.END


async def receive_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Получает username и парсит аватарку
    """
    username = update.message.text.strip().lstrip('@')

    if not username:
        await update.message.reply_text(
            '❌ Username не может быть пустым!\n'
            'Попробуйте ещё раз или используйте /start'
        )
        return WAITING_USERNAME

    # Отправляем сообщение о начале поиска
    status_message = await update.message.reply_text(
        f'🔍 Ищу аватарку для @{username}...\n'
        'Это может занять несколько секунд.'
    )

    try:
        # Получаем URL аватарки
        avatar_url = get_tiktok_avatar_url(username)

        if not avatar_url:
            await status_message.edit_text(
                f'❌ Не удалось найти аватарку для @{username}\n\n'
                'Возможные причины:\n'
                '• Неправильный username\n'
                '• Профиль приватный\n'
                '• Профиль не существует\n\n'
                'Используйте /start для нового поиска.'
            )
            return ConversationHandler.END

        await status_message.edit_text('📥 Скачиваю аватарку...')

        # Скачиваем аватарку
        avatar_path = download_avatar_to_temp(avatar_url)

        if not avatar_path:
            await status_message.edit_text(
                '❌ Ошибка при скачивании аватарки.\n'
                'Попробуйте позже или используйте /start'
            )
            return ConversationHandler.END

        # Отправляем аватарку
        await status_message.edit_text('✅ Отправляю аватарку...')

        with open(avatar_path, 'rb') as photo:
            await update.message.reply_photo(
                photo=photo,
                caption=f'✅ Аватарка @{username}\n\n'
                        f'Используйте /start для нового поиска.'
            )

        # Удаляем сообщение о статусе
        await status_message.delete()

        # Удаляем временный файл
        os.unlink(avatar_path)

    except Exception as e:
        await status_message.edit_text(
            f'❌ Произошла ошибка: {str(e)}\n\n'
            'Попробуйте позже или используйте /start'
        )
        print(f"Ошибка: {e}")

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Отмена текущей операции
    """
    await update.message.reply_text(
        '❌ Операция отменена.\n'
        'Используйте /start для возврата в меню.'
    )
    return ConversationHandler.END


def main():
    """
    Запуск бота
    """
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()

    # ConversationHandler для обработки диалога
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

    # Добавляем обработчики
    application.add_handler(conv_handler)

    # Запускаем бота
    print("🤖 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()