from bot.filetocloud import CloudBot, filters
import subprocess
import shlex
import os

AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

@CloudBot.on_message(filters.command("exec") & filters.private & filters.user(AUTHORIZED_USERS))
async def execute_command(client, message):

    # Extracting the command from the message
    command = message.text.split(" ", 1)
    if len(command) < 2:
        await message.reply_text("Please provide a command to execute.")
        return

    command = command[1]

    try:
        # Splitting the command into shell-true command
        args = shlex.split(command)
        # Executing the command
        output = subprocess.run(args, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        # Sending back the output
        response_message = f"Output:\n{output.stdout}"
    except subprocess.CalledProcessError as e:
        response_message = f"Error:\n{e.stderr}"
    except Exception as e:
        response_message = f"Failed to execute command. Error: {str(e)}"

    # Ensure the message is not too long for Telegram
    if len(response_message) > 4096:
        response_message = response_message[:4090] + "\n... (output truncated)"

    await message.reply_text(response_message)