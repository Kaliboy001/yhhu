import asyncio
import aiohttp
import json
import os
from pyrogram import Client, filters
import logging
from aiohttp import ClientTimeout

# Set up logging to catch any bullshit errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot credentials - your fucking API shit
API_ID = 15787995
API_HASH = "e51a3154d2e0c45e5ed70251d68382de"
BOT_TOKEN = "7929166887:AAHlObbpll0ZD0U0xjgOmAFi1gWiYOW_eGQ"

# The API URL for downloading media
BASE_API_URL = "https://taitan-medi-downloader.taitanapi.workers.dev/down?url="

# Initialize the bot client
app = Client("media_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Async function to fetch media from the API with retries and headers
async def fetch_media(url, retries=1, timeout=8):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession(timeout=ClientTimeout(total=timeout), headers=headers) as session:
                api_url = f"{BASE_API_URL}{url}"
                async with session.get(api_url) as response:
                    if response.status != 200:
                        return None, f"API fucked up with status {response.status}"
                    data = await response.json()
                    return data, None
        except Exception as e:
            if attempt == retries - 1:
                return None, f"Shit hit the fan: {str(e)}"
            await asyncio.sleep(0.3)
    return None, "Fuck, retries failed."

# Function to select the best video quality (not audio)
def select_best_video(medias):
    for media in medias:
        if "audio" not in media["quality"].lower():
            return media["url"]
    return None

# Handler for any text message (assumes it’s a URL)
@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_url(client, message):
    url = message.text.strip()
    if not url.startswith("http"):
        await message.reply_text("That’s not a fucking URL, dumbass. Send a proper link!")
        return

    # Simple processing message
    processing_message = await message.reply_text("Your video is processing, you’ll receive it in a sec, wait")

    # Fetch the media from the API
    data, error = await fetch_media(url)
    if error or not data:
        await processing_message.edit_text(f"Fuck, something went wrong: {error or 'No data, asshole.'}")
        return

    # Extract the title and media list
    title = data.get("title", "No fucking title")
    medias = data.get("medias", [])

    if not medias:
        await processing_message.edit_text("No fucking media found, you moron.")
        return

    # Select the best video
    video_url = select_best_video(medias)
    if not video_url:
        await processing_message.edit_text("No fucking video, just audio crap.")
        return

    # Download and send the video
    temp_file = f"temp_video_{message.chat.id}.mp4"
    try:
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=20), headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}) as session:
            async with session.get(video_url) as response:
                if response.status != 200:
                    await processing_message.edit_text(f"Download fucked up with status {response.status}")
                    return
                with open(temp_file, "wb") as f:
                    async for chunk in response.content.iter_chunked(2048 * 1024):  # 2MB chunks
                        f.write(chunk)
                await message.reply_video(video=temp_file, caption=f"Here’s your fucking video: {title}")
                os.remove(temp_file)
    except Exception as e:
        await processing_message.edit_text(f"Shit broke: {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

    await processing_message.delete()

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    await message.reply_text("Yo, I’m your fucking media downloader bot! Send me a goddamn social media link, and I’ll grab the video for you. Let’s fucking do this!")

# Start the bot
if __name__ == "__main__":
    logger.info("Starting the fucking bot...")
    app.run()
