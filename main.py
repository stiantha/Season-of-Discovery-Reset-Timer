import os
from typing import Final
from discord import Intents, Client, Activity, ActivityType
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
import schedule
import time
import threading
import math
from datetime import datetime, timedelta
import pytz


load_dotenv()

TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# STEP 1: BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# Define the timezone for the reset time
reset_timezone = pytz.timezone('Europe/Oslo')  # Norway timezone

def job():
    # Get the current time in the reset timezone
    now = datetime.now(reset_timezone)

    if now.weekday() >= 4:  # If today is Friday, Saturday, or Sunday
        # Calculate the last Friday
        days_behind = now.weekday() - 4  # 4 represents Friday
    else:
        # Calculate the last Tuesday
        days_behind = now.weekday() - 1  # 1 represents Tuesday

    if days_behind < 0:  # If today is Monday or Tuesday (for Tuesday calculation) or Friday (for Friday calculation)
        days_behind += 7  # Get the last Tuesday or Friday

    last_reset_time = now - timedelta(days=days_behind)
    last_reset_time = last_reset_time.replace(hour=5, minute=0, second=0, microsecond=0)

    # Calculate the next reset time
    if now - last_reset_time > timedelta(hours=72):
        next_reset_time = last_reset_time + timedelta(days=7)
    else:
        next_reset_time = last_reset_time + timedelta(days=3)

    # Calculate the remaining time until the next reset
    remaining_time = next_reset_time - now
    remaining_hours = math.ceil(remaining_time.total_seconds() / 3600)  # Convert to hours and round up

    # Set the bot's status to the remaining time
    activity = Activity(name=f"in {remaining_hours} hours", type=ActivityType.playing)
    asyncio.run_coroutine_threadsafe(client.change_presence(activity=activity), client.loop)

# wow timer reset
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    job()  # Change the bot's nickname when the bot is ready
    print(f'{client.user} is now running!')
    # Schedule the job to run every 25 minutes
    schedule.every(25).minutes.do(job)

# STEP 5: MAIN ENTRY POINT
def main() -> None:
    # Run the client in a separate thread
    threading.Thread(target=client.run, args=(TOKEN,)).start()

    while True:
        # Run pending jobs
        schedule.run_pending()
        # Sleep for a while before checking for pending jobs again
        time.sleep(1)


if __name__ == '__main__':
    main()