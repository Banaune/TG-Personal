import psutil
from pyrogram import Client, filters
import time
import datetime
from bot.filetocloud import CloudBot
from bot import state

@CloudBot.on_message(filters.command("stats"))
async def send_stats(client, message):
    # Calculate uptime
    uptime_seconds = time.time() - state.bot_start_time
    uptime_string = str(datetime.timedelta(seconds=int(uptime_seconds)))

    # System's uptime
    system_uptime_seconds = psutil.boot_time()
    system_uptime_string = str(datetime.timedelta(seconds=int(time.time() - system_uptime_seconds)))

    # Ping time
    start_time = time.time()
    await client.get_me()
    end_time = time.time()
    ping_time = round((end_time - start_time) * 1000, 2)  # Ping time in milliseconds

    # CPU usage and load
    cpu_usage = psutil.cpu_percent()
    cpu_load_1, cpu_load_5, cpu_load_15 = psutil.getloadavg()  # System load over the last 1, 5, and 15 minutes

    # Memory usage
    memory = psutil.virtual_memory()
    memory_usage = memory.percent
    total_memory_gb = round(memory.total / (1024**3), 2)
    used_memory_gb = round(memory.used / (1024**3), 2)
    available_memory_gb = round(memory.available / (1024**3), 2)
    free_memory_gb = round(memory.free / (1024**3), 2)

    # Disk usage
    disk = psutil.disk_usage('/')
    total_disk_gb = round(disk.total / (1024**3), 2)
    used_disk_gb = round(disk.used / (1024**3), 2)
    free_disk_gb = round(disk.free / (1024**3), 2)

    # Prepare the detailed stats message
    stats_message = (
        f"🤖 Bot Uptime: {uptime_string}\n"
        f"💻 System Uptime: {system_uptime_string}\n"
        f"🏓 Ping: {ping_time}ms\n"
        f"🖥 CPU Usage: {cpu_usage}%\n"
        f"📈 CPU Load: 1min {cpu_load_1}, 5min {cpu_load_5}, 15min {cpu_load_15}\n"
        f"💾 Memory Usage: {memory_usage}% (Used: {used_memory_gb}GB / Total: {total_memory_gb}GB)\n"
        f"🔍 Memory Available: {available_memory_gb}GB, Free: {free_memory_gb}GB\n"
        f"🗄 Storage Usage: (Used: {used_disk_gb}GB / Total: {total_disk_gb}GB, Free: {free_disk_gb}GB)"
    )

    # Send the detailed stats message
    await message.reply_text(stats_message)