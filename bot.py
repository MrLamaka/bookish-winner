import time
import asyncio
from collections import deque
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

import nest_asyncio
nest_asyncio.apply()

# 🔑 Токен и ID канала
BOT_TOKEN = "7697561078:AAEtpC1MhWQ3v6k9yzaCQiLLYgy_fGb2ISA"
CHANNEL_ID = -1002267481727  # Замени на ID своего канала

# ⏳ Кулдаун
COOLDOWN = 120  # секунд

# 🥒 Очередь сообщений
message_queue = deque()
last_sent_time = 0

# 📥 Обработка входящих сообщений
async def forward_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_sent_time

    if not update.message:
        return

    now = time.time()
    time_since_last = now - last_sent_time
    time_left = COOLDOWN - time_since_last

    message_queue.append(update.message)

    if time_left > 0:
        await update.message.reply_text(
            f"Сообщение получено. До следующей отправки в канал осталось {int(time_left)} секунд."
        )
    else:
        await update.message.reply_text(
            "Сообщение получено и будет сразу отправлено в канал.\n✅ Вы уже можете снова отправить сообщение."
        )

# 📤 Отправка сообщений в канал
async def send_to_channel(bot, message):
    try:
        if message.text:
            await bot.send_message(chat_id=CHANNEL_ID, text=message.text)
        elif message.photo:
            await bot.send_photo(chat_id=CHANNEL_ID, photo=message.photo[-1].file_id, caption=message.caption or "")
        elif message.video:
            await bot.send_video(chat_id=CHANNEL_ID, video=message.video.file_id, caption=message.caption or "")
        elif message.document:
            await bot.send_document(chat_id=CHANNEL_ID, document=message.document.file_id, caption=message.caption or "")
        elif message.audio:
            await bot.send_audio(chat_id=CHANNEL_ID, audio=message.audio.file_id, caption=message.caption or "")
        elif message.voice:
            await bot.send_voice(chat_id=CHANNEL_ID, voice=message.voice.file_id)
        else:
            await bot.send_message(chat_id=CHANNEL_ID, text="(неподдерживаемый тип сообщения)")
    except Exception as e:
        print(f"Ошибка при отправке в канал: {e}")

# ⏲️ Обработка очереди с кулдауном
async def queue_worker(app):
    global last_sent_time
    while True:
        now = time.time()
        if message_queue and (now - last_sent_time >= COOLDOWN):
            message = message_queue.popleft()
            await send_to_channel(app.bot, message)
            last_sent_time = now
        await asyncio.sleep(1)

# 🚀 Запуск бота
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_message))
    asyncio.create_task(queue_worker(app))
    print("Бот запущен в режиме polling...")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
