import os
import telebot
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove
from yt_dlp import YoutubeDL
from dotenv import load_dotenv
import logging
import time
# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()
# Load environment variables from .env file (Replit Secret storage)
load_dotenv()
# Bot initialization
API_TOKEN = os.getenv('7469377685:AAE9CpFZfXd4xmjvxQMqf4UkI-E2Bp3VNkY')
bot = telebot.TeleBot(API_TOKEN)
# Store user's current download URL
user_links = {}
# Ensure downloads directory exists
os.makedirs('downloads', exist_ok=True)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "YouTube, Instagram yoki TikTok linkini yuboring.")


@bot.message_handler(
    func=lambda message: message.text.startswith(('http://', 'https://')))
def handle_url(message):
    url = message.text.strip()
    # Store URL for this user
    user_links[message.chat.id] = url
    # Create keyboard markup
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add('🎵 Musiqa', '🎥 Video')
    bot.reply_to(message, "Formatni tanlang:", reply_markup=markup)


@bot.message_handler(
    func=lambda message: message.text in ['🎵 Musiqa', '🎥 Video'])
def handle_format(message):
    url = user_links.get(message.chat.id)
    if not url:
        bot.reply_to(message, "Iltimos, avval link yuboring.")
        return
    # Debugging: Log the user ID and URL
    logger.debug(
        f"User {message.chat.id} selected {message.text} with URL {url}")
    # Send loading message and remove keyboard
    bot.send_message(message.chat.id,
                     "⏳ Yuklanmoqda...",
                     reply_markup=ReplyKeyboardRemove())
    try:
        if message.text == '🎵 Musiqa':
            download_audio(message.chat.id, url)
        else:
            download_video(message.chat.id, url)
    except Exception as e:
        # Error handling: Log and send error message to user
        logger.error(f"Error in handle_format: {str(e)}")
        bot.send_message(message.chat.id, f"Xatolik yuz berdi: {str(e)}")


def download_audio(chat_id, url):
    opts = {
        'format':
        'bestaudio/best',
        'outtmpl':
        'downloads/%(title)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'
            # Check if file exists and send the audio
            if os.path.exists(file_path):
                with open(file_path, 'rb') as audio:
                    bot.send_audio(
                        chat_id,
                        audio.read())  # Use .read() to send audio file content
                os.remove(file_path)  # Clean up the file after sending
                logger.info(f"Audio sent successfully to {chat_id}.")
            else:
                logger.error(f"Audio file not found: {file_path}")
            del user_links[chat_id]
    except Exception as e:
        logger.error(f"Error in download_audio: {str(e)}")
        bot.send_message(chat_id, f"Yuklab olishda xatolik: {str(e)}")


def download_video(chat_id, url):
    # Fetch Instagram credentials from environment variables
    instagram_username = os.getenv(
        'Yordamchiaccount')  # Your Instagram username
    instagram_password = os.getenv('Kirish1009')  # Your Instagram password
    # Check if credentials are available
    if not instagram_username or not instagram_password:
        logger.error("Instagram credentials missing.")
        bot.send_message(
            chat_id,
            "Instagram login credentials are missing. Please provide them.")
        return
    opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'username': instagram_username,
        'password': instagram_password,
        'quiet': True,
    }
    try:
        with YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            file_path = ydl.prepare_filename(info)
            time.sleep(2)  # Add a 2-second delay between requests
            # Check if file exists and send the video
            if os.path.exists(file_path):
                with open(file_path, 'rb') as video:
                    bot.send_video(
                        chat_id,
                        video.read())  # Use .read() to send video file content
                os.remove(file_path)  # Clean up the file after sending
                logger.info(f"Video sent successfully to {chat_id}.")
            else:
                logger.error(f"Video file not found: {file_path}")
            del user_links[chat_id]
    except Exception as e:
        logger.error(f"Error in download_video: {str(e)}")
        bot.send_message(chat_id, f"Yuklab olishda xatolik: {str(e)}")


# Polling to keep the bot running
bot.polling(none_stop=True)

#API 7469377685:AAE9CpFZfXd4xmjvxQMqf4UkI-E2Bp3VNkY
#Instagram Yordamchiaccount Kirish1009
