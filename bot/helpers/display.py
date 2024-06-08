from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import timedelta, datetime
from bot import LOGGER, state

logger = LOGGER(__name__)

last_edit_time = {}

async def progress(current, total, message: Message = None, user_message: Message = None, operation: str = "download"):
    operation_title = "Uploading" if operation == "upload" else "Downloading"
    completion_message = "Upload completed" if operation == "upload" else "Download completed"

    download_id = f"{message.chat.id}{message.id}"
    print("Progress Download ID++++++++++++++++++++:", download_id)
    start_time = state.get_start_time(download_id, default=time.perf_counter())
    if state.download_status.get(download_id) == "cancelled":
        state.remove_start_time(download_id)
        raise Exception("Download cancelled.")

    if current == total:
        await user_message.edit(text=completion_message)
        state.remove_start_time(download_id)
        state.download_status[download_id] = "completed"
        return

    now = datetime.now()
    if not state.is_time_to_update(download_id, now):
        return  # Skip this update to avoid hitting the rate limit

    # Simulate some operation
    time.sleep(0.000001)
    time_diff = max(time.perf_counter() - start_time, 0.01)
    percent = round(current * 100 / total, 2)
    progress_str = progressBar(percent)
    speed = float(current) / time_diff/1024
    eta = timedelta(seconds=int((total - current) / speed)) if speed > 0 else "Unknown"
    elapsed = timedelta(seconds=int(time_diff))


    progress_details = (
        f"{operation_title}...\n"
        f"{progress_str} {percent}%\n"
        f"{human_readable_size(current)} of {human_readable_size(total)}\n"
        f"Speed: {human_readable_size(speed)}/s\n"
        f"ETA: {eta}\n"
        f"Elapsed: {elapsed}"
    )

    try:
        await user_message.edit(
            text=progress_details,
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("Cancel!", callback_data=f"cncl+{download_id}")]]
            )
        )
        state.update_last_edit_time(download_id, now)
    except Exception as e:
        logger.error(f"Error updating progress: {e}")

def progressBar(percent):
    done_block = '█'
    empty_block = '░'
    done_blocks = int(percent // 5)
    empty_blocks = 20 - done_blocks
    return f"{done_block * done_blocks}{empty_block * empty_blocks}"

def human_readable_size(size, decimal_places=2):
    for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
        if size < 1024.0:
            break
        size /= 1024.0
    return f"{size:.{decimal_places}f} {unit}"