#fr0gg.py
import discord
from discord.ext import commands

import os
from dotenv import load_dotenv

import random
from datetime import datetime

import aiohttp
import cloudinary
import cloudinary.uploader
import asyncio

from send_email import gmail_service, create_message, send_message
from firebaseDB_add import insert_data_to_firebase

load_dotenv()

# Process environment variables.
bot_token = os.environ.get('TOKEN')
cloud = os.environ.get('CLOUD_NAME')
cloudinary_api = os.environ.get('CLOUDINARY_API_KEY')
cloudinary_api_secret = os.environ.get('CLOUDINARY_API_SECRET')

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
  cloud_name = cloud, 
  api_key = cloudinary_api, 
  api_secret = cloudinary_api_secret 
)

# Possible values for prompts.
location_list = ["Puerto Rico", "Jamaica", "Texas", "Dominican Republic", "Ghana", "Barbados", "Cuba", "Florida", "Brazil", "Costa Rica"]
artist_list = ["Joan Miro", "Juan Gris", "Mike Kelley", "Robert Rauschenberg", "Willem deKooning", "Cecily Brown", "Piet Mondrian", "Karel Appel", "Haim Steinbach", "Pablo Picasso", "Philip Guston", "Henry Moore", "Isamu Noguchi", "Alexander Calder", "Barbara Hepworth", "Jean Arp", "Leon Golub","Jeff Koons","Constant Nieuwenhuys", "Asger Jorn", "Jenny Saville", "Paul McCarthy" , "Paul Klee", "Mark Rothko"]
species_list = ["Agalychnis callidryas", "Dendrobates auratus", "Dendrobates tinctorius", "Hyalinobatrachium ruedai", "Dendrobates azureus", "Breviceps macrops", "Conraua goliath", "Theloderma corticale", "Nasikabatrachus sahyadrensis", "Pipa pipa", "Rhacophorus nigropalmatus", "Ceratophrys genus"]

# Global variables
thread_id = None
upload_date = datetime.now().strftime("%m/%d/%Y")
location = random.choice(location_list)
artists = random.sample(artist_list, 2)
species = random.choice(species_list)
prompt = f'{species}, a cute small ceramic frog sculpture, souvenir from a trip to {location}, full-color, {artists[0]}, {artists[1]}, textured white background, highly textured Xerox scan, archival museum catalog --no text, base, plinth  --stylize 750 --v 3'

class ConsoleStyles:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# Print messages to console with a timestamp.
def print_with_timestamp(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{ConsoleStyles.OKGREEN}{ConsoleStyles.BOLD}{timestamp}{ConsoleStyles.ENDC} {message}")

# Create a new prompt.
async def create_prompt():
  global thread_id
  global prompt
  global upload_date
  
  # Get the appropriate channel.
  channel = discord.utils.get(bot.get_all_channels(), name='sandbox')
  
  if channel:
      # Create a new thread for today's date.
      thread = await channel.create_thread(name=upload_date, auto_archive_duration=60)
      
      # Update the thread ID.
      thread_id = thread.id
      
      # Send today's prompt to the thread.
      prompt_message = await thread.send(prompt)
      
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
      email_message = create_message('info@0-p.us', 'josephrvalle@gmail.com', "today's fr0.gg - {upload_date}", message_link)
      send_message(service, 'me', email_message)
      print_with_timestamp("E-mail sent.")
  else:
      print_with_timestamp("Channel not found.") 
      
async def daily_task():
  global upload_date
  while True:
      now = datetime.now()
      # Run the task daily at midnight (00:00)
      if now.hour == 2 and now.minute == 0:
          print_with_timestamp(f"Creating a new prompt for {upload_date}.")
          await create_prompt()
          await asyncio.sleep(90)  # Sleep for 90 seconds after task execution
      else:
          await asyncio.sleep(60)  # Check every minute
          
@bot.event
async def on_ready():
    print_with_timestamp(f'Successfully logged in as {bot.user}')
    bot.loop.create_task(daily_task())
    
# For testing purposes.
@bot.command(name='testfunctions')
async def test_functions(ctx):
    await create_prompt()
    
@bot.command(name="newprompt")
async def random_prompt(ctx):
  print_with_timestamp("Creating new prompt.")
  await ctx.send( f'{random.choice(species_list)}, a cute small ceramic frog sculpture, souvenir from a trip to {random.choice(location_list)}, full-color, {random.choice(artist_list)},  {random.choice(artist_list)}, textured white background, highly textured Xerox scan, archival museum catalog --no text, base, plinth  --stylize 750 --v 3')
 

        
@bot.command(name='saveimage')
async def save_image(ctx):
    global thread_id
    global prompt
    global upload_date
    
    print_with_timestamp("Command received to save image.")
    
    # Check if a thread has been created.
    if thread_id is None:
        await ctx.send("No thread created yet.")
        return

    # Check for the correct channel.
    channel = bot.get_channel(thread_id)
    if channel is None:
        await ctx.send("Thread channel not found.")
        return
      
    # Find upscaled image.
    async for message in channel.history(limit=100, oldest_first=False):
        
        # Midjourney bot ID from this server.
        midjourney_bot_id = 936929561302675456
        
        if message.author.id == midjourney_bot_id and message.attachments:
            image_url = message.attachments[0].url
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
                    firebase_result = insert_data_to_firebase(upload_date, prompt, cloudinary_result["url"])
                    
                    await ctx.send(f"Successfully uploaded today's fr0gg.")
                    await ctx.send("See you tomorrow! 🐸")
                    print_with_timestamp("Image successfully uploaded to Cloudinary and link added to Firebase.")
                    return
                    
    if not found_image:
        await ctx.send("No image saved, please try again.")
        
@bot.command(name='upload')
async def save_image(ctx):
    await ctx.send("Stand by...")
  
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