from pyrogram.types import Message
from bot import LOGGER, state, cloudscraper_instance
from ..filetocloud import CloudBot
from .display import progress
import time
import os
from tqdm import tqdm

logger = LOGGER(__name__)

async def download_media(client: CloudBot, message: Message) -> str:
    download_id = f"{message.chat.id}{message.id}"
    state.download_controller[download_id] = False  # Initialize cancellation flag
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



async def download_file_cloudscraper(url, filename, message: Message) -> tuple:
    download_id = f"{message.chat.id}{message.id}"
    state.download_controller[download_id] = False  # Initialize cancellation flag
    try:
        # Create 'downloads' directory if it doesn't exist
        os.makedirs('downloads', exist_ok=True)

        # Join 'downloads' with the filename
        filename = os.path.join('downloads', filename)
        response = cloudscraper_instance.get(url, stream=True)
        response.raise_for_status()
        message = await message.edit_text("Downloading started...")

        total_size_in_bytes = int(response.headers.get('content-length', 0))
        progress_bar = tqdm(total=total_size_in_bytes, unit='iB', unit_scale=True)


        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                progress_bar.update(len(chunk))
                f.write(chunk)

                # Update the progress bar with the progress of writing the file to disk
                written_size_in_bytes = os.path.getsize(filename)
                await progress(progress_bar.n, total_size_in_bytes, user_message=message, operation="download")
                progress_bar.set_postfix(file=f"{written_size_in_bytes / total_size_in_bytes * 100:.2f}%", refresh=True)
        progress_bar.close()

        if total_size_in_bytes != 0 and progress_bar.n != total_size_in_bytes:
            logger.error("ERROR, something went wrong")

        logger.info(f"File downloaded successfully: {filename}")
        return filename, True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return None, False