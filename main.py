import asyncio
import aiohttp
import json
import os
from pyrogram import Client, filters
import logging
from aiohttp import ClientTimeout
import time

# Set up logging to catch any bullshit errors
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bot credentials
API_ID = 15787995
API_HASH = "e51a3154d2e0c45e5ed70251d68382de"
BOT_TOKEN = "7929166887:AAEk33TiL46qYqOiMmiK0XLlvDW-iZnVQgg"

# The API URL for downloading media
BASE_API_URL = "https://taitan-medi-downloader.taitanapi.workers.dev/down?url="

# Initialize the bot client
app = Client("media_downloader_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Rate limiting to avoid Telegram spam
last_message_time = 0
RATE_LIMIT_SECONDS = 2  # 2 seconds between messages to be safe

# Async function to fetch media from the API with retries and headers
async def fetch_media(url, retries=2, timeout=10):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept": "*/*",
        "Referer": "https://www.youtube.com/"
    }
    for attempt in range(retries):
        try:
            async with aiohttp.ClientSession(timeout=ClientTimeout(total=timeout), headers=headers) as session:
                api_url = f"{BASE_API_URL}{url}"
                async with session.get(api_url) as response:
                    if response.status != 200:
                        return None, f"API error: status {response.status}"
                    data = await response.json()
                    return data, None
        except Exception as e:
            if attempt == retries - 1:
                return None, f"API fetch failed: {str(e)}"
            await asyncio.sleep(1)
    return None, "API retries exhausted."

# Function to select the best video quality
def select_best_video(medias, url):
    # Detect platform from URL
    is_youtube = "youtube.com" in url or "youtu.be" in url
    is_tiktok = "tiktok.com" in url
    is_facebook = "facebook.com" in url

    for media in medias:
        quality = media["quality"].lower()
        # Skip audio
        if "audio" in quality:
            continue
        # YouTube: Prioritize mp4, highest resolution
        if is_youtube and "mp4" in quality:
            return media["url"]
        # TikTok: Prioritize no_watermark
        elif is_tiktok and "no_watermark" in quality:
            return media["url"]
        # Facebook: Prioritize HD
        elif is_facebook and "hd" in quality:
            return media["url"]
        # Default: Take the first non-audio video
        elif "audio" not in quality:
            return media["url"]
    return None

# Handler for any text message (assumes it’s a URL)
@app.on_message(filters.text & ~filters.command(["start"]))
async def handle_url(client, message):
    global last_message_time

    # Rate limiting to prevent spam
    current_time = time.time()
    if current_time - last_message_time < RATE_LIMIT_SECONDS:
        await asyncio.sleep(RATE_LIMIT_SECONDS - (current_time - last_message_time))
    last_message_time = time.time()

    url = message.text.strip()
    # Strict URL validation
    if not (url.startswith("http://") or url.startswith("https://")) or len(url) < 10:
        await message.reply_text("Send a proper fucking URL, asshole!")
        return

    # Simple processing message
    processing_message = await message.reply_text("Processing your video, wait a sec...")

    # Fetch the media from the API
    data, error = await fetch_media(url)
    if error or not data:
        await processing_message.edit_text(f"Error: {error or 'No data found.'}")
        return

    # Extract media list
    medias = data.get("medias", [])
    if not medias:
        await processing_message.edit_text("No media found in the link.")
        return

    # Select the best video
    video_url = select_best_video(medias, url)
    if not video_url:
        await processing_message.edit_text("No video found, only audio.")
        return

    # Download and send the video
    temp_file = f"temp_video_{message.chat.id}.mp4"
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Accept": "*/*",
            "Referer": "https://www.youtube.com/" if "youtube.com" in url or "youtu.be" in url else url
        }
        async with aiohttp.ClientSession(timeout=ClientTimeout(total=40), headers=headers) as session:
            async with session.get(video_url) as response:
                if response.status != 200:
                    await processing_message.edit_text(f"Download failed: status {response.status}")
                    return
                with open(temp_file, "wb") as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                        f.write(chunk)
                # Send the video, no caption
                await message.reply_video(video=temp_file)
                os.remove(temp_file)
    except Exception as e:
        await processing_message.edit_text(f"Download/upload error: {str(e)}")
        if os.path.exists(temp_file):
            os.remove(temp_file)

    await processing_message.delete()

# Command handler for /start
@app.on_message(filters.command("start"))
async def start_command(client, message):
    global last_message_time
    current_time = time.time()
    if current_time - last_message_time < RATE_LIMIT_SECONDS:
        await asyncio.sleep(RATE_LIMIT_SECONDS - (current_time - last_message_time))
    last_message_time = time.time()

    await message.reply_text("Send a social media link, I’ll download the video. Let’s fucking go!")

# Start the bot
if __name__ == "__main__":
    logger.info("Starting the bot...")
    app.run()
