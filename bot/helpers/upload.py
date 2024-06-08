import os
import time
import logging
import mimetypes
from pyrogram import errors, Client
from pyrogram.types import Message
from bot import state
from .display import progress

async def upload_file_to_telegram(client: Client, message: Message, file_path: str):
    """
    Uploads a file to Telegram using a Pyrogram client.

    Args:
        client (pyrogram.Client): The Pyrogram client.
        message (pyrogram.types.Message): The message to reply to.
        file_path (str): The path to the file.

    Raises:
        ValueError: If the file does not exist.
    """
    # Ensure the file exists
    if not os.path.exists(file_path):
        raise ValueError(f"File does not exist: {file_path}")

    # Initialize the upload status
    upload_id = f"{message.chat.id}{message.id}"
    state.upload_controller[upload_id] = False  # Initialize cancellation flag

    user_message = await message.edit_text("Starting Upload...")

    try:
        await user_message.edit_text("Uploading started...")
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type and mime_type.startswith('video'):
            await client.send_video(
                chat_id=message.chat.id,
                video=file_path,
                progress=progress,
                progress_args=(message, user_message,)  # Pass user_message to progress
            )
        else:
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                progress=progress,
                progress_args=(message, user_message,)  # Pass user_message to progress
            )
            await user_message.delete()
            if state.upload_status.get(upload_id) == "cancelled":
                print("Upload cancelled.")
                await user_message.edit_text("Upload cancelled.")
                return None, False
            return file_path, True
    except errors.FloodWait as e:
        # Handle the FloodWait exception, which is raised when we're being rate-limited
        logging.warning(f"Being rate-limited. Sleeping for {e.x} seconds.")
        time.sleep(e.x)
        return upload_file_to_telegram(client, message, file_path)  # Retry uploading the file after sleeping
    except errors.RPCError as e:
        # Handle general API errors
        logging.error(f"Failed to upload file due to API error: {e}")
        await user_message.edit_text("An error occurred.")
        return None, False
    except Exception as e:
        # Handle unexpected exceptions
        logging.error(f"An unexpected error occurred: {e}")
        await user_message.edit_text("An error occurred.")
        return None, False
    finally:
        # Clean up the cancellation flag
        if upload_id in state.upload_controller:
            del state.upload_controller[upload_id]
        if upload_id in state.upload_status:
            del state.upload_status[upload_id]