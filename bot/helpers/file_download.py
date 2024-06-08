from pyrogram.types import Message
from bot import LOGGER, state
from ..filetocloud import CloudBot
from .display import progress

logger = LOGGER(__name__)

async def download_media(client: CloudBot, message: Message) -> str:
    download_id = f"{message.chat.id}{message.id}"
    state.download_controller[download_id] = False  # Initialize cancellation flag

    user_message = await client.send_message(
        chat_id=message.from_user.id,
        reply_to_message_id=message.id,
        text="Processing your request...",
    )
    try:
        await user_message.edit_text("Downloading started...")
        download_file_path = await client.download_media(
            message,
            progress=progress,
            progress_args=(message, user_message,)  # Pass user_message to progress
        )
        await user_message.delete()
        if state.download_status.get(download_id) == "cancelled":
            print("Download cancelled.")
            await user_message.edit_text("Download cancelled.")
            return None, False
        return download_file_path, True
    except Exception as e:
        logger.error(e)
        await user_message.edit_text("An error occurred.")
        return None, False
    finally:
        # Clean up the cancellation flag
        if download_id in state.download_controller:
            del state.download_controller[download_id]
        if download_id in state.download_status:
            del state.download_status[download_id]