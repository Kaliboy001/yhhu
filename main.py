import asyncio
import re
import aiohttp
from telethon import TelegramClient, events
from telethon.tl.types import DocumentAttributeVideo
import uuid
import os

# Bot configuration - Replace with your actual credentials
API_ID = '15787995'  # Get from my.telegram.org
API_HASH = 'e51a3154d2e0c45e5ed70251d68382de'  # Get from my.telegram.org
BOT_TOKEN = '6947943234:AAGeX30scbhBm5LTOo0fjYD8RFv8Yyzdk6M'  # Get from @BotFather
API_URL = 'https://taitan-medi-downloader.taitanapi.workers.dev/down?url='

# Initialize Telegram client with optimizations
client = TelegramClient('bot', API_ID, API_HASH, connection_retries=3, timeout=10)

# Broad URL validation pattern for multiple platforms
PLATFORM_REGEX = r'(https?://)?(www\.)?(youtube\.com|youtu\.be|instagram\.com|facebook\.com|tiktok\.com)/.+$'

async def fetch_video_info(url):
    """Fetch media information from the API with timeout."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL + url, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                return None
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return None

async def stream_download(video_url, file_name):
    """Stream download the media to a file with smaller chunks."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(video_url, timeout=30) as response:
                if response.status != 200:
                    return False
                with open(file_name, 'wb') as f:
                    async for chunk in response.content.iter_chunked(1024 * 1024):  # 1MB chunks
                        f.write(chunk)
                return True
    except (aiohttp.ClientError, asyncio.TimeoutError):
        return False

@client.on(events.NewMessage(pattern=PLATFORM_REGEX))
async def handle_media_link(event):
    """Handle media URL messages from various platforms and send video directly."""
    media_url = event.message.text
    chat_id = event.chat_id
    
    # Send processing message
    processing_msg = await event.reply("Processing... ⏳")
    
    # Fetch media information
    media_info = await fetch_video_info(media_url)
    
    if not media_info or 'medias' not in media_info:
        await client.send_message(chat_id, "Couldn't process this link. Try another.")
        await processing_msg.delete()
        return
    
    # Select the first available video quality
    video_medias = [m for m in media_info['medias'] if m['quality'].lower() not in ('audio', 'sd')]
    if not video_medias:
        video_medias = [m for m in media_info['medias'] if not m['quality'].lower() == 'audio']
    if not video_medias:
        await client.send_message(chat_id, "No video available for this link.")
        await processing_msg.delete()
        return
    
    selected_media = video_medias[0]
    title = media_info['title'].replace('/', '_')  # Sanitize title for filename
    duration = int(sum(int(x) * 60 ** i for i, x in enumerate(reversed(media_info['duration'].split(':'))))) if ':' in media_info['duration'] else int(media_info['duration'])
    
    # Stream download the video
    file_name = f"{title[:50]}_{uuid.uuid4().hex}.mp4"  # Limit title length to avoid filename issues
    success = await stream_download(selected_media['url'], file_name)
    
    if not success or not os.path.exists(file_name):
        await client.send_message(chat_id, "Failed to download. Try again.")
        await processing_msg.delete()
        if os.path.exists(file_name):
            os.remove(file_name)
        return
    
    # Send video to user with title in filename
    await client.send_file(
        chat_id,
        file_name,
        attributes=[DocumentAttributeVideo(duration=duration, w=640, h=360)]
    )
    
    # Clean up
    os.remove(file_name)
    await processing_msg.delete()

async def main():
    """Start the bot with reconnection handling."""
    await client.start(bot_token=BOT_TOKEN)
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
