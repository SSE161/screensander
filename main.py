import keyboard
import mss
import threading
import asyncio
from PIL import ImageGrab
from telegram import Bot, Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# Токен Telegram-бота
TOKEN = "your token"
bot = Bot(token=TOKEN)
gpt_token = ""


# Тут будет сохраняться chat_id
chat_id_holder = {"chat_id": None}
event_loop_holder = {"loop": None}

async def send_screenshot_async():
    chat_id = chat_id_holder["chat_id"]
    if not chat_id:
        print("⚠️ Пользователь ещё не написал боту.")
        return

    screenshot = ImageGrab.grab()
    screenshot.save("screen.png", quality=95)

    with open("screen.png", "rb") as f:
        await bot.send_photo(chat_id=chat_id, photo=f)
        print("✅ Скриншот отправлен!")

def send_screenshot():
    loop = event_loop_holder["loop"]
    if loop is None:
        print("❌ Event loop ещё не инициализирован.")
        return
    loop.call_soon_threadsafe(lambda: asyncio.create_task(send_screenshot_async()))


# 📥 Обработчик входящих сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not chat_id_holder["chat_id"]:
        chat_id_holder["chat_id"] = chat_id
        await update.message.reply_text("📸 Привет! Теперь я могу отправлять тебе скриншоты.")
        print(f"🔗 chat_id сохранён: {chat_id}")
    else:
        await update.message.reply_text("✅ Я уже знаю твой chat_id. не пиши мне больше")

# 👂 Запуск Telegram-бота в отдельном потоке

def start_telegram_bot():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    event_loop_holder["loop"] = loop  # 💾 сохраняем loop
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Telegram-бот запущен.")
    app.run_polling()


# ▶ Запуск бота и горячей клавиши
if __name__ == "__main__":
    # Поток Telegram-бота
    bot_thread = threading.Thread(target=start_telegram_bot, daemon=True)
    bot_thread.start()

    print("⌨️ Ожидаю нажатия F8 для скриншота...")
    keyboard.add_hotkey('F8', send_screenshot)

    try:
        while True:
            pass  # Бесконечное ожидание
    except KeyboardInterrupt:
        print("🛑 Завершено пользователем.")
