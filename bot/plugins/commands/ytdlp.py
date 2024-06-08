from bot.filetocloud import CloudBot, filters
import subprocess
import shlex
import os
from bot import LOGGER, state
import re
import asyncio
from bot.helpers.upload import upload_file_to_telegram

logger = LOGGER(__name__)

AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

def get_filename(url):
    command = ["yt-dlp", "--restrict-filenames", "--get-filename", "-o", "%(title)s.%(ext)s", url]
    process = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    return process.stdout.strip()

def download_video(url):
    command = ["yt-dlp", "--newline", "--restrict-filenames", "-o", "downloads/%(title)s.%(ext)s", url]
    process = subprocess.run(command)

async def download_video_explicit(url: str, message) -> tuple:
    download_id = f"{message.chat.id}{message.id}"
    state.download_controller[download_id] = False  # Initialize cancellation flag
    try:
        filename = get_filename(url)
        await message.edit(f"Downloading video...\n{filename}")
        download_video(url)
        return filename, None
    except Exception as e:
        logger.error(e)
        return None, e

@CloudBot.on_message(filters.command("ytdlp") & filters.private & filters.user(AUTHORIZED_USERS))
async def ytdlp(client, message):
    url = message.text.split(" ", 1)[1]
    user_message = await message.reply(text="Downloading video...", reply_to_message_id=message.id)
    filename, error = await download_video_explicit(url, user_message)
    logger.info(f"Downloaded video: {filename}")
    if error:
        await message.reply(f"An error occurred: {error}")
        return
    await user_message.edit(f"Downloaded video: {filename}")
    filename_with_path = f"downloads/{filename}"
    logger.info(f"Uploading video: {filename_with_path}")
    await upload_file_to_telegram(client, user_message, filename_with_path)
    os.remove(filename_with_path)
    await user_message.delete()