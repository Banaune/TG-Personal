from bot.filetocloud import CloudBot, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot import CLEAR_AUTH
from bot.env import clear_auth
import os

AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

@CloudBot.on_message(filters.command("clear_auth") & filters.private & filters.user(AUTHORIZED_USERS))
async def clear_auth_command(client, message):
    confirm_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Confirm", callback_data="confirm_clear_auth"),
         InlineKeyboardButton("Cancel", callback_data="cancel_clear_auth")]
    ])
    # Store the message ID for later deletion
    global message_to_delete
    message_to_delete = message.id
    await client.send_message(
        chat_id=message.chat.id,
        text="Are you sure you want to clear the authentication tokens???????????",
        reply_markup=confirm_markup,
        reply_to_message_id=message.id,
    )

@CloudBot.on_callback_query(filters.regex("^confirm_clear_auth$"))
async def confirm_clear_auth(client, callback_query):
    if clear_auth():
        response_text = CLEAR_AUTH
    else:
        response_text = "Failed to clear the authentication tokens."
    
    await client.answer_callback_query(callback_query.id, response_text)
    print("Authentication tokens cleared.")
    # Delete the original command message and the confirmation message
    await client.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=[callback_query.message.id, message_to_delete]
    )

@CloudBot.on_callback_query(filters.regex("^cancel_clear_auth$"))
async def cancel_clear_auth(client, callback_query):
    # Inform the user that the operation was cancelled
    await client.answer_callback_query(callback_query.id, "Clear authentication cancelled.")
    print("Clear authentication cancelled.")
    # Delete the original command message and the confirmation message
    await client.delete_messages(
        chat_id=callback_query.message.chat.id,
        message_ids=[callback_query.message.id, message_to_delete]
    )