import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes
from telegram.ext import filters

# توکن ربات تلگرام
TOKEN = "6947943234:AAGeX30scbhBm5LTOo0fjYD8RFv8Yyzdk6M"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 به ربات دانلود خوش آمدید!\nلینک پست اینستاگرام، اسپاتیفای، تیک‌تاک، یوتیوب یا فیسبوک را ارسال کنید.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    bot = context.bot

    # اینستاگرام
    if message.text and message.text.startswith("https://www.instagram.com"):
        url1 = f"https://api.fast-creat.ir/instagram?apikey=6105815457:jnChxURtvyMI65e@Api_ManagerRoBot&type=post&url={message.text}"
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

        try:
            response = requests.get(url1)
            response.raise_for_status()
            data = response.json()

            if data.get("ok") and data.get("status") == "successfully":
                results = data.get("result", [])
                if not results:
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text="نتیجه‌ای یافت نشد.",
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )
                else:
                    last_item = results[-1]
                    if last_item:
                        is_video = last_item.get("is_video", False)
                        caption = last_item.get("caption", "")
                        
                        if is_video:
                            await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")
                            video_url = last_item.get("video_url")
                            if video_url:
                                await bot.send_video(
                                    chat_id=message.chat.id,
                                    video=video_url,
                                    caption=caption,
                                    reply_to_message_id=message.message_id
                                )
                            else:
                                await bot.send_message(
                                    chat_id=message.chat.id,
                                    text="لینک ویدئو یافت نشد.",
                                    parse_mode="HTML",
                                    reply_to_message_id=message.message_id
                                )
                        else:
                            await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
                            photo_url = last_item.get("image_url")
                            if photo_url:
                                await bot.send_photo(
                                    chat_id=message.chat.id,
                                    photo=photo_url,
                                    caption=caption,
                                    reply_to_message_id=message.message_id
                                )
                            else:
                                await bot.send_message(
                                    chat_id=message.chat.id,
                                    text="لینک عکس یافت نشد.",
                                    parse_mode="HTML",
                                    reply_to_message_id=message.message_id
                                )
            else:
                await bot.send_message(
                    chat_id=message.chat.id,
                    text="خطا در دریافت اطلاعات از سرور.",
                    parse_mode="HTML",
                    reply_to_message_id=message.message_id
                )
        except Exception as e:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"<b>خطا رخ داد:</b> {str(e)}",
                parse_mode="HTML",
                reply_to_message_id=message.message_id
            )

    # اسپاتیفای
    elif message.text and message.text.startswith("https://open.spotify.com"):
        url1 = f"https://open.wiki-api.ir/apis-2/DownloadSpotify?link={message.text}"
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")

        try:
            response = requests.get(url1)
            response.raise_for_status()
            data = response.json()

            if data.get('status') and data.get('results'):
                results = data['results']
                name = results.get('name', 'نام موجود نیست')
                track_name = results.get('track_name', 'نام آهنگ موجود نیست')
                release_date = results.get('release_date', 'تاریخ انتشار موجود نیست')
                image = results.get('image', None)
                artist_url = results.get('artist_url', None)
                album_url = results.get('album_url', None)
                media = results.get('media', None)

                caption = (
                    f"‍‍‍\n<b>نام:</b> {name}\n"
                    f"<b>آهنگ:</b> {track_name}\n"
                    f"<b>تاریخ انتشار:</b> {release_date}\n"
                    f"<b>لینک هنرمند:</b> <a href='{artist_url}'>مشاهده</a>\n"
                    f"<b>لینک آلبوم:</b> <a href='{album_url}'>مشاهده</a>"
                )

                if image:
                    await bot.send_photo(
                        chat_id=message.chat.id,
                        photo=image,
                        caption=caption,
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )
                else:
                    await bot.send_message(
                        chat_id=message.chat.id,
                        text=caption,
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )

                if media:
                    await bot.send_chat_action(chat_id=message.chat.id, action="upload_audio")
                    await bot.send_audio(
                        chat_id=message.chat.id,
                        audio=media,
                        caption=f"{track_name}",
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )
        except Exception as e:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"خطا در پردازش لینک اسپاتیفای: {e}",
                reply_to_message_id=message.message_id
            )

    # تیک‌تاک
    elif message.text and (message.text.startswith("https://vt.tiktok.com") or message.text.startswith("https://www.tiktok.com")):
        url1 = f"https://haji-api.ir/tiktok/?license=9Wu97449YSQUAV7034576996382305168wdas&url={message.text}"
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

        try:
            response = requests.get(url1)
            response.raise_for_status()
            data = response.json()

            if data.get('ok') and data.get('result'):
                result = data['result']
                title = result.get('title', 'عنوان موجود نیست')
                media = result.get('media', None)

                if media:
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=media,
                        caption=f"<b>عنوان:</b> {title}",
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )
        except Exception as e:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"خطا در پردازش لینک تیک‌تاک: {e}",
                reply_to_message_id=message.message_id
            )

    # یوتیوب
    elif message.text and (message.text.startswith("https://youtu") or message.text.startswith("https://www.youtube.com")):
        url1 = f"https://tele-social.vercel.app/down?url={message.text}"
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

        try:
            response = requests.get(url1)
            response.raise_for_status()
            data = response.json()

            if data.get('status') and data.get('video'):
                video_url = data['video']
                audio_url = data.get('audio', '')
                title = data.get('title', 'عنوان موجود نیست')
                duration = data.get('quality', 'کیفیت موجود نیست')
                description = data.get('desc', 'توضیحات موجود نیست')
                thumbnail = data.get('thumb', None)

                try:
                    # Send video first
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=video_url,
                        caption=f"‍‍‍‌‌\n<b>عنوان:</b> {title}\n<b>کیفیت:</b> {duration}\n<b>توضیحات:</b> {description}",
                        parse_mode="HTML",
                        reply_to_message_id=message.message_id
                    )
                    
                        
                except Exception as e:
                    if thumbnail:
                        keyboard = [
                            [InlineKeyboardButton("دانلود ویدیو", url=video_url)],
                            [InlineKeyboardButton("دانلود موزیک", url=audio_url)] if audio_url else []
                        ]
                        await bot.send_photo(
                            chat_id=message.chat.id,
                            photo=thumbnail,
                            caption=f"\n<b>عنوان:</b> {title}\n<b>کیفیت:</b> {duration}\n<b>توضیحات:</b> {description}",
                            parse_mode="HTML",
                            reply_markup=InlineKeyboardMarkup(keyboard),
                            reply_to_message_id=message.message_id
                        )
        except Exception as e:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"خطا در پردازش لینک یوتیوب: {e}",
                reply_to_message_id=message.message_id
            )

    # فیسبوک
    elif message.text and message.text.startswith("https://www.facebook.com"):
        url1 = f"https://facebookdl.apinepdev.workers.dev/?url={message.text}"
        await bot.send_chat_action(chat_id=message.chat.id, action="upload_video")

        try:
            response = requests.get(url1)
            response.raise_for_status()
            data = response.json()

            if data.get('success'):
                video_link = data.get('hdlink') or data.get('sdlink')
                if video_link:
                    await bot.send_video(
                        chat_id=message.chat.id,
                        video=video_link,
                        reply_to_message_id=message.message_id
                    )
        except Exception as e:
            await bot.send_message(
                chat_id=message.chat.id,
                text=f"خطا در پردازش لینک فیسبوک: {e}",
                reply_to_message_id=message.message_id
            )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
