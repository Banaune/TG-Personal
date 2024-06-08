import os
import shutil
from bot.filetocloud import CloudBot, filters

DOWNLOADS_FOLDER_PATH = 'bot/downloads'

AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

@CloudBot.on_message(filters.command("clear_downloads") & filters.private & filters.user(AUTHORIZED_USERS))
async def clear_downloads_command(client, message):
    try:
        # Check if the downloads folder exists
        if os.path.exists(DOWNLOADS_FOLDER_PATH) and os.path.isdir(DOWNLOADS_FOLDER_PATH):
            # Remove all contents of the downloads folder
            for filename in os.listdir(DOWNLOADS_FOLDER_PATH):
                file_path = os.path.join(DOWNLOADS_FOLDER_PATH, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Failed to delete {file_path}. Reason: {e}')
            await client.send_message(chat_id=message.chat.id, text="Downloads folder cleared.")
        else:
            await client.send_message(chat_id=message.chat.id, text="Downloads folder does not exist.")
    except Exception as e:
        await client.send_message(chat_id=message.chat.id, text=f"Failed to clear downloads folder. Reason: {e}")