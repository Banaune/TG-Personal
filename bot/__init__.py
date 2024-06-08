#!/usr/bin/env python3
import os
import logging
from .env import get_env
from logging.handlers import RotatingFileHandler
import time
import cloudscraper

API_ID = get_env('API_ID')
API_HASH = get_env('API_HASH')
BOT_TOKEN = get_env('BOT_TOKEN')

print("API_ID:", API_ID, "API_HASH", API_HASH, "BOT_TOKEN", BOT_TOKEN)

class GlobalState:
    def __init__(self):
        self.start_times = {}
        self.last_edit_times = {}
        self.upload_controller = {}
        self.download_controller = {}
        self.bot_start_time = time.time()
        self.download_status = {}
        self.upload_status = {}

    def get_start_time(self, download_id, default=None):
        return self.start_times.get(download_id, default)

    def set_start_time(self, download_id, start_time):
        self.start_times[download_id] = start_time

    def remove_start_time(self, download_id):
        if download_id in self.start_times:
            del self.start_times[download_id]

    def update_last_edit_time(self, download_id, edit_time):
        self.last_edit_times[download_id] = edit_time

    def is_time_to_update(self, download_id, now):
        if download_id not in self.last_edit_times:
            self.last_edit_times[download_id] = now
            return True
        last_edit = self.last_edit_times[download_id]
        if (now - last_edit).total_seconds() > 5:  # Adjust the threshold as needed
            return True
        return False

# Create a global instance of the state
state = GlobalState()


# Messages
START = "\n\n**~~This bot uploads telegram files to Dropbox. \n\n**"
ERROR = "Something went wrong\n{error}"
HELP = "\n\nUsage: **Send any file. Then select the third-party Cloud you want to upload to.**"
CLEAR_AUTH = "Authentication tokens have been cleared."


# LOGGER

# Ensure the directory exists
LOGGER_FILE_NAME = "Downloads.log"
log_dir = os.path.dirname(os.path.abspath(__file__))
log_file_path = os.path.join(log_dir, LOGGER_FILE_NAME)
os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    handlers=[
        RotatingFileHandler(
            log_file_path,
            maxBytes=1024 * 1024 * 10,  # 10 MB
            backupCount=5
        ),
        logging.StreamHandler()
    ])
logging.getLogger('pyrogram').setLevel(logging.WARNING)


def LOGGER(log: str) -> logging.Logger:
    """Logger function"""
    return logging.getLogger(log)

cloudscraper_instance = cloudscraper.create_scraper()
