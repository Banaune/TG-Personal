from ...filetocloud import CloudBot, filters
from bot import LOGGER
import os
from bot.helpers.getLink import telegram_bot_function as process_url, general_download_and_upload as upload_handler
import pyrogram
from pyrogram.types import Message
from pyrogram.enums import MessageEntityType

AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

VIDEO = filters.video & filters.user(AUTHORIZED_USERS)
DOCUMENT = filters.document & filters.user(AUTHORIZED_USERS)
AUDIO = filters.audio & filters.user(AUTHORIZED_USERS)
AUTHORIZED = filters.user(AUTHORIZED_USERS)

logger = LOGGER(__name__)

@CloudBot.on_message(AUTHORIZED)
async def get_link(client, bot: Message):
    logger.info(f"\n{bot.chat.id} - {bot.text} \n{bot.caption}")
    if bot.text:
        user_message = await bot.reply_text(text="Processing...", reply_to_message_id=bot.id)
        await user_message.edit("Checking for links...")
        urls = check_for_urls_and_return_urls(bot)
        if urls:
            for url in urls:
                is_terabox = check_for_terabox_link(url)
                if is_terabox:
                    try:
                        await user_message.edit("TeraBox link detected. Processing...")
                    except pyrogram.errors.exceptions.bad_request_400.MessageIdInvalid:
                        user_message = await bot.reply_text(text="TeraBox link detected. Processing...", reply_to_message_id=bot.id)
                    link = await process_url(url, client, user_message)
                else:
                    try:
                        await user_message.edit("Processing link...\n" + url)
                    except pyrogram.errors.exceptions.bad_request_400.MessageIdInvalid:
                        user_message = await bot.reply_text(text="Processing link...", reply_to_message_id=bot.id)
                    link = await upload_handler(url, client, user_message)
        else:
            await user_message.edit("No link found in the message.")

def check_for_terabox_link(url):
    if "tera" in url:
        return True
    return False

# Check if there are any urls in the message and return them
def check_for_urls_and_return_urls(message: Message):
    urls = []
    if message.entities:
        for entity in message.entities:
            if entity.type == MessageEntityType.URL:
                url = message.text[entity.offset:entity.offset + entity.length]
                logger.info(f"URL found: {url}")
                urls.append(url)
    return urls
    