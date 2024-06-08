import psutil
import platform
from pyrogram import Client, filters
from datetime import datetime
from pyrogram import enums
from bot.filetocloud import CloudBot
import os


AUTHORIZED_USERS = [int(user_id) for user_id in os.environ.get("AUTHORIZED_USERS", "").split()]

@CloudBot.on_message(filters.command("system_info") & filters.private & filters.user(AUTHORIZED_USERS))
async def system_info(client, message):
    # System-wide information
    uname = platform.uname()
    system_info = f"💻 <b>System</b>: <i>{uname.system}</i>\n"
    system_info += f"🖥 <b>Node Name</b>: <i>{uname.node}</i>\n"
    system_info += f"📀 <b>Release</b>: <i>{uname.release}</i>\n"
    system_info += f"🔖 <b>Version</b>: <i>{uname.version}</i>\n"
    system_info += f"🛠 <b>Machine</b>: <i>{uname.machine}</i>\n"
    system_info += f"🔧 <b>Processor</b>: <i>{uname.processor}</i>\n\n"

    # Boot Time
    boot_time_timestamp = psutil.boot_time()
    bt = datetime.fromtimestamp(boot_time_timestamp)
    system_info += f"⏰ <b>Boot Time</b>: <i>{bt.year}/{bt.month}/{bt.day} {bt.hour}:{bt.minute}:{bt.second}</i>\n\n"

    # CPU information
    cpufreq = psutil.cpu_freq()
    system_info += f"🧮 <b>Physical cores</b>: <i>{psutil.cpu_count(logical=False)}</i>\n"
    system_info += f"💾 <b>Total cores</b>: <i>{psutil.cpu_count(logical=True)}</i>\n"
    system_info += f"🚀 <b>Max Frequency</b>: <i>{cpufreq.max:.2f}Mhz</i>\n"
    system_info += f"🐢 <b>Min Frequency</b>: <i>{cpufreq.min:.2f}Mhz</i>\n"
    system_info += f"⚡ <b>Current Frequency</b>: <i>{cpufreq.current:.2f}Mhz</i>\n"
    system_info += f"📊 <b>CPU Usage</b>: <i>{psutil.cpu_percent()}%</i>\n\n"

    # RAM Usage
    svmem = psutil.virtual_memory()
    system_info += f"🧠 <b>Total Memory</b>: <i>{svmem.total / (1024 ** 3):.2f} GB</i>\n"
    system_info += f"🔋 <b>Available Memory</b>: <i>{svmem.available / (1024 ** 3):.2f} GB</i>\n"
    system_info += f"💽 <b>Used Memory</b>: <i>{svmem.used / (1024 ** 3):.2f} GB</i>\n"
    system_info += f"📈 <b>Memory Usage</b>: <i>{svmem.percent}%</i>\n\n"

    # Disk Information
    partitions = psutil.disk_partitions()
    for partition in partitions:
        system_info += f"📦 === Device: <i>{partition.device}</i> ===\n"
        system_info += f"🗄 <b>Mountpoint</b>: <i>{partition.mountpoint}</i>\n"
        system_info += f"💾 <b>File system type</b>: <i>{partition.fstype}</i>\n"
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
            system_info += f"📚 <b>Total Size</b>: <i>{partition_usage.total / (1024 ** 3):.2f} GB</i>\n"
            system_info += f"📉 <b>Used</b>: <i>{partition_usage.used / (1024 ** 3):.2f} GB</i>\n"
            system_info += f"📈 <b>Free</b>: <i>{partition_usage.free / (1024 ** 3):.2f} GB</i>\n"
            system_info += f"🔋 <b>Percentage</b>: <i>{partition_usage.percent}%</i>\n"
        except (PermissionError, OSError) as e:
            # Handle locked BitLocker drives or other OS errors
            system_info += f"🚫 <b>Error accessing drive</b>: <i>{e}</i>\n"

    # Sending the system information with HTML parse mode support
    await message.reply_text(system_info, parse_mode=enums.ParseMode.HTML)
