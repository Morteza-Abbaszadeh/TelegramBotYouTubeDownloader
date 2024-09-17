import telebot
from pytubefix import YouTube
from pytubefix.cli import on_progress
import os

# Replace with your actual Telegram bot token
TOKEN = 'your_token'
bot = telebot.TeleBot(TOKEN)

# Directory to save downloaded files
DOWNLOAD_DIR = 'downloads'
MAX_FILE_SIZE_MB = 50  # Maximum file size in MB

# Ensure the download directory exists
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Send me a YouTube URL and I will download and send the video.')

@bot.message_handler(func=lambda message: True)  # Handle all text messages
def handle_download_command(message):
    url = message.text
    if url:
        try:
            yt = YouTube(url, on_progress_callback=on_progress)
            video_title = yt.title
            bot.reply_to(message, f'Downloading video: {video_title}')
            
            # Download the video
            ys = yt.streams.get_highest_resolution()
            video_file_path = os.path.join(DOWNLOAD_DIR, f'{video_title}.mp4')
            ys.download(output_path=DOWNLOAD_DIR, filename=f'{video_title}.mp4')

            # Check file size
            file_size_mb = os.path.getsize(video_file_path) / (1024 * 1024)  # Convert bytes to MB
            if file_size_mb > MAX_FILE_SIZE_MB:
                bot.reply_to(message, f'The file is too large to send. The size of the video is {file_size_mb:.2f} MB.')
                os.remove(video_file_path)  # Optionally delete the file
                return

            # Send the video file to the user
            with open(video_file_path, 'rb') as video_file:
                bot.send_video(message.chat.id, video_file, caption=video_title)
            
            # Optionally delete the file after sending
            os.remove(video_file_path)
        except Exception as e:
            bot.reply_to(message, f'Error: {str(e)}')
    else:
        bot.reply_to(message, 'Please provide a valid YouTube URL.')

# Polling to keep the bot running
bot.polling()
