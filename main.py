import os
import json
from typing import Final
from discord import Intents, Client, Activity, ActivityType
from datetime import datetime, timedelta
from dotenv import load_dotenv
import asyncio
import schedule
import time
import threading
import math
import pytz

load_dotenv()

TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')

# BOT SETUP
intents: Intents = Intents.default()
intents.message_content = True  # NOQA
client: Client = Client(intents=intents)

# Define the timezone for the reset time
reset_timezone = pytz.timezone('Europe/Oslo')  # Norway timezone

def job():
    # Get the current time in the reset timezone
    now = datetime.now(reset_timezone)

    # Try to read the next reset time from the file
    try:
        with open('next_reset_time.json', 'r') as f:
            next_reset_time = datetime.fromisoformat(json.load(f))
    except (FileNotFoundError, ValueError):
        # If the file doesn't exist or contains invalid data, use a default next reset time
        next_reset_time = datetime.fromisoformat(os.getenv('NEXT_RESET_TIME'))

    # If the next reset time has passed, calculate the next reset time
    if now >= next_reset_time:
        next_reset_time = now + timedelta(hours=72)
        # Store the next reset time in the file
        with open('next_reset_time.json', 'w') as f:
            json.dump(next_reset_time.isoformat(), f)

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

# MAIN ENTRY POINT
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