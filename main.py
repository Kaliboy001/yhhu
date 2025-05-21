import asyncio
import aiohttp
import json
import os
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import logging

# Set up logging to catch any bullshit errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot credentials - your fucking API shit
API_ID = 15787995
API_HASH = "e51a3154d2e0c45e5ed70251d68382de"
BOT_TOKEN = "7929166887:AAFO20E0MW1hz0J0jiyCPxNu1YYfmPCvBuQ"

# The API URL for downloading media
BASE_API_URL = "https://taitan-medi-downloader.taitanapi.workers.dev/down?url="

# Initialize the bot client
app = Client("media_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Async function to fetch media from the API
async def fetch_media(url):
    async with aiohttp.ClientSession() as session:
        api_url = f"{BASE_API_URL}{url}"
        try:
            async with session.get(api_url) as response:
                if response.status != 200:
                    return None, f"API fucked up with status {response.status}"
                data = await response.json()
                return data, None
        except Exception as e:
            return None, f"Shit hit the fan while fetching: {str(e)}"

# Function to select the best video quality (not audio)
def select_best_video(media_list):
    for media in media_list:
        if "audio" not in media["quality"].lower():
            return media["url"]
    return None

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Yo, I’m your fucking media downloader bot! Send me a goddamn social media link (Instagram, TikTok, Facebook, YouTube, whatever), and I’ll grab the video for you. Let’s fucking do this!")

# Handler for any text message (assumes it’s a URL)
@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_url(client, message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.reply_text("That’s not a fucking URL, dumbass. Send a proper link!")
        return

    # Send a "processing" message to keep the user from bitching
    processing_message = await message.reply_text("Hold on, I’m fucking processing your shit...")

    # Fetch the media from the API
    data, error = await fetch_media(url)
    if error or not data:
        await processing_message.edit_text(f"Fuck, something went wrong: {error or 'No data, asshole.'}")
        return

    # Extract the title and media list
    title = data.get("title", "No fucking title")
    medias = data.get("medias", [])

    if not medias:
        await processing_message.edit_text("No fucking media found in this link, you moron.")
        return

    # Select the best video quality
    video_url = select_best_video(medias)
    if not video_url:
        await processing_message.edit_text("Couldn’t find a fucking video in this shit. Only audio or some crap.")
        return

    # Edit the processing message to show we’re downloading
    await processing_message.edit_text(f"Got it! Title: {title}. Now downloading the fucking video...")

    # Download the video and save it temporarily
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url) as response:
                if response.status != 200:
                    await processing_message.edit_text(f"Download fucked up, server said no with status {response.status}")
                    return

                # Save the video to a temp file
                temp_file = f"temp_video_{message.chat.id}.mp4"
                with open(temp_file, "wb") as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)

                # Upload the video from the temp file
                await processing_message.edit_text("Uploading the goddamn video to you now...")
                await message.reply_video(video=temp_file, caption=f"Here’s your fucking video: {title}")

                # Clean up the temp file
                os.remove(temp_file)

        # Delete the processing message after success
        await processing_message.delete()

    except Exception as e:
        await processing_message.edit_text(f"Shit broke while downloading/uploading: {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

# Start the bot
if __name__ == "__main__":
    logger.info("Starting the fucking bot...")
    app.run()
