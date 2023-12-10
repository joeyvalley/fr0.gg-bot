#!/usr/bin/env python3
import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

import random, re
from datetime import datetime

import aiohttp
import cloudinary
import cloudinary.uploader
import asyncio

from send_email import gmail_service, create_message, send_message
from firebaseDB_add import insert_data_to_firebase

load_dotenv()

# Process environment variables.
bot_token = os.environ.get("TOKEN")
cloud = os.environ.get("CLOUD_NAME")
cloudinary_api = os.environ.get("CLOUDINARY_API_KEY")
cloudinary_api_secret = os.environ.get("CLOUDINARY_API_SECRET")

# Setup intents for Discord bot
intents = discord.Intents.default()
intents.messages = True
intents.guild_messages = True
intents.presences = True
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Configure Cloudinary for image uploading.
cloudinary.config(
    cloud_name=cloud, api_key=cloudinary_api, api_secret=cloudinary_api_secret
)

# Possible values for prompts.
location_list = [
    "Puerto Rico",
    "Jamaica",
    "Texas",
    "Dominican Republic",
    "Ghana",
    "Barbados",
    "Cuba",
    "Florida",
    "Brazil",
    "Costa Rica",
]
artist_list = [
    "Joan Miro",
    "Juan Gris",
    "Mike Kelley",
    "Robert Rauschenberg",
    "Willem deKooning",
    "Cecily Brown",
    "Piet Mondrian",
    "Karel Appel",
    "Haim Steinbach",
    "Pablo Picasso",
    "Philip Guston",
    "Henry Moore",
    "Isamu Noguchi",
    "Alexander Calder",
    "Barbara Hepworth",
    "Jean Arp",
    "Leon Golub",
    "Jeff Koons",
    "Constant Nieuwenhuys",
    "Asger Jorn",
    "Jenny Saville",
    "Paul McCarthy",
    "Paul Klee",
    "Mark Rothko",
]
species_list = [
    "Agalychnis callidryas",
    "Dendrobates auratus",
    "Dendrobates tinctorius",
    "Hyalinobatrachium ruedai",
    "Dendrobates azureus",
    "Breviceps macrops",
    "Conraua goliath",
    "Theloderma corticale",
    "Nasikabatrachus sahyadrensis",
    "Pipa pipa",
    "Rhacophorus nigropalmatus",
    "Ceratophrys genus",
]
qualities_list = ["cute", "simple", "angry", "devilish", "smiling", "fat"]
firing_styles = [
    "raku-fired",
    "pit-fired",
    "soda-fired",
    "salt-fired",
    "oxidation fired",
    "reduction fired",
    "bisque-fired",
    "wood-fired",
]

# Global variables
thread_id = None
upload_date = datetime.now().strftime("%Y-%m-%d")
prompt_message = ""

# Add to log file.
dir_path = os.path.dirname(os.path.realpath(__file__))
log_path = os.path.join(dir_path, "logs", "logfile.txt")
with open(log_path, "a") as f:
    f.write(f'Script started at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.\n')


class ConsoleStyles:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# Print messages to console with a timestamp.
def print_with_timestamp(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(
        f"{ConsoleStyles.OKGREEN}{ConsoleStyles.BOLD}{timestamp}{ConsoleStyles.ENDC} {message}"
    )


def extract_prompt(text):
    pattern = r"\*\*(.*?)\*\*"
    match = re.search(pattern, text)
    if match:
        return match.group(1)
    else:
        return ""


def prompt():
    location = random.choice(location_list)
    artists = random.sample(artist_list, 2)
    species = random.choice(species_list)
    firing_style = random.choice(firing_styles)
    quality = random.choice(qualities_list)
    return f"a small {quality} ceramic frog sculpture, {firing_style}, {species}, souvenir from {location}, full-color photograph, {artists[0]}, {artists[1]}, textured white background, highly textured Xerox scan, archival museum catalog --no text, base, plinth  --stylize 750 --v 3"


# Create a new prompt.
async def create_prompt():
    global thread_id
    global upload_date
    global prompt_message

    # Update date.
    upload_date = datetime.now().strftime("%Y-%m-%d")

    # Get the appropriate channel.
    channel = discord.utils.get(bot.get_all_channels(), name="sandbox")

    if channel:
        # Create a new thread for today's date.
        thread = await channel.create_thread(name=upload_date, auto_archive_duration=60)

        # Update the thread ID.
        thread_id = thread.id

        # Send today's prompt to the thread.
        prompt_message = await thread.send(prompt())

        # Add Midjourney bot to the thread.
        user_id = 936929561302675456
        user = await bot.fetch_user(user_id)
        if user:
            mention_message = await thread.send(user.mention)

        else:
            await thread.send("Cannot find Midjourney bot.")
            return

        # Email link to today's thread.
        message_link = f"https://discord.com/channels/{channel.guild.id}/{thread.id}/{prompt_message.id}"
        service = gmail_service()
        email_message = create_message(
            "info@0-p.us",
            "josephrvalle@gmail.com",
            f"Today's fr0.gg - {upload_date}",
            message_link,
        )
        send_message(service, "me", email_message)
        print_with_timestamp("E-mail sent.")
    else:
        print_with_timestamp("Channel not found.")


async def daily_task():
    global upload_date
    while True:
        now = datetime.now()
        # Run the task daily at 2AM.
        if now.hour == 2 and now.minute == 0:
            print_with_timestamp(f"Creating a new prompt for {upload_date} at {now}.")
            await create_prompt()
            await asyncio.sleep(6000)  # Sleep for 90 seconds after task execution
        else:
            await asyncio.sleep(60)  # Check every minute


@bot.event
async def on_ready():
    print_with_timestamp(f"Successfully logged in as {bot.user}")
    bot.loop.create_task(daily_task())


# Test that daily tasks are working.
@bot.command(name="test")
async def test_functions(ctx):
    print_with_timestamp("Command received to test functions.")
    await create_prompt()


# Check that today's date is correct.
@bot.command(name="today")
async def test_date(ctx):
    global upload_date
    print_with_timestamp("Command received to test date.")
    await ctx.send(f"Today's date is {upload_date}")


# Check that today's date is correct.
@bot.command(name="now")
async def test_time(ctx):
    now = datetime.now()
    print_with_timestamp("Command received to test time.")
    print_with_timestamp(f"It is {now.hour}:{now.minute}")
    await ctx.send(f"It is {now.hour}:{now.minute}")


#
@bot.command(name="email")
async def test_email(ctx):
    print_with_timestamp("Command received to test email function.")
    service = gmail_service()
    email_message = create_message(
        "info@0-p.us",
        "josephrvalle@gmail.com",
        "Test E-mail",
        "Test",
    )
    message = send_message(service, "me", email_message)
    print_with_timestamp(f'Message ID: {message["id"]}')


# Create a prompt in direct messages.
@bot.command(name="prompt")
async def random_prompt(ctx):
    print_with_timestamp("Command received to create new prompt.")
    global prompt_message
    prompt_message = await ctx.send(prompt())


# Save image and upload to the database.
@bot.command(name="save")
async def save_image(ctx):
    global thread_id
    global prompt_message
    global upload_date

    print_with_timestamp("Command received to save image.")

    # If thread_id is None, use the channel where the command was issued.
    if thread_id is None:
        print_with_timestamp(
            "Error: No specific thread set. Using the current channel."
        )
        channel = ctx.channel
    else:
        # Check for the correct channel.
        channel = bot.get_channel(thread_id)
        if channel is None:
            print_with_timestamp("Error: Thread channel not found.")
            await ctx.send("Thread channel not found.")
            return

    # Find upscaled image.
    found_image = False
    async for message in channel.history(limit=100, oldest_first=False):
        # Midjourney bot ID from this server.
        midjourney_bot_id = 936929561302675456

        if message.author.id == midjourney_bot_id and message.attachments:
            image_url = message.attachments[0].url
            prompt_message = extract_prompt(message.content)
            found_image = True
            break

    if found_image:
        print_with_timestamp("Upscaled image located in thread.")
        async with aiohttp.ClientSession() as session:
            async with session.get(image_url) as response:
                if response.status == 200:
                    # Upload image to Cloudinary.
                    image_data = await response.read()
                    cloudinary_result = cloudinary.uploader.upload(image_data)
                    # Insert data into Firebase.
                    firebase_result = insert_data_to_firebase(
                        upload_date, prompt_message, cloudinary_result["url"]
                    )
                    await ctx.send(f"Successfully uploaded today's fr0gg.")
                    await ctx.send("See you tomorrow! 🐸")
                    print_with_timestamp(
                        "Image successfully uploaded to Cloudinary and added to Firebase."
                    )
                # If there is an error with the aiohttp function.
                else:
                    print_with_timestamp(f"{response}")

    if not found_image:
        await ctx.send("No image saved, please try again.")


@bot.event
# Prevent fr0.gg from talking to itself in a feedback loop.
async def on_message(message):
    if message.author == bot.user:
        return
    # Allow fr0.gg to process custom commands.
    await bot.process_commands(message)

    # Be cute with it.
    if isinstance(message.channel, discord.DMChannel):
        # Respond to the DM
        await message.channel.send("ribbit 🐸")


bot.run(bot_token)
