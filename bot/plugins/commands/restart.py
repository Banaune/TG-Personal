import sys
from bot.filetocloud import CloudBot, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

@CloudBot.on_message(filters.command("restart") & filters.private & filters.user(AUTHORIZED_USERS))
async def ask_restart(client, message):
    restart_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm Restart", callback_data="confirm_restart"),
         InlineKeyboardButton("Cancel", callback_data="cancel_restart")]
    ])
    await client.send_message(
        chat_id=message.chat.id,
        text="Are you sure you want to restart the bot?",
        reply_markup=restart_markup,
        reply_to_message_id=message.id,
    )

@CloudBot.on_callback_query(filters.regex("^confirm_restart$"))
async def restart(client, callback_query):
    await client.answer_callback_query(callback_query.id, "Restarting the bot...")
    # Delete the original message
    await client.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=[callback_query.message.id]
    )
    # Restart the bot by exiting the process
    sys.exit(42)

@CloudBot.on_callback_query(filters.regex("^cancel_restart$"))
async def cancel_restart(client, callback_query):
    await client.answer_callback_query(callback_query.id, "Restart cancelled.")
    # Delete the original message
    await client.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=[callback_query.message.id]
    )