import schedule
import datetime
import asyncio
from discord.ext import tasks
from datetime import datetime, timedelta

def job(client):
    # Get the current time
    now = datetime.now()
    # Calculate the last Tuesday at 04:00
    days_behind = now.weekday() - 1  # 1 represents Tuesday
    if days_behind < 0:  # If today is Monday
        days_behind += 7  # Get the last Tuesday
    last_reset_time = now - timedelta(days=days_behind)
    last_reset_time = last_reset_time.replace(hour=4, minute=0, second=0, microsecond=0)
    # Calculate the next reset time
    if now - last_reset_time > timedelta(hours=72):
        next_reset_time = last_reset_time + timedelta(days=7)
    else:
        next_reset_time = last_reset_time + timedelta(days=3)
    # Format the time as a string
    next_reset_time_str = next_reset_time.strftime("TEST%A %H:%M")
    # Change the bot's nickname to the next reset time
    for guild in client.guilds:
        asyncio.run_coroutine_threadsafe(guild.me.edit(nick=next_reset_time_str), client.loop)
    # Schedule the job to run again at the next reset time
    delay = (next_reset_time - now).total_seconds()
    schedule.every(delay).seconds.do(lambda: job(client))